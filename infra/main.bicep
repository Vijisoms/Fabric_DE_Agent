targetScope = 'resourceGroup'

@description('Name of the environment. Used to derive resource names.')
param environmentName string

@description('Azure region for resources.')
param location string

var resourceToken = uniqueString(subscription().id, resourceGroup().id, location, environmentName)

// Resource names: az{prefix}{token}
var acrName = take('azacr${resourceToken}', 32)
var uamiName = take('azid${resourceToken}', 32)
var logName = take('azlog${resourceToken}', 32)
var caeName = take('azcae${resourceToken}', 32)
var caName = take('azca${resourceToken}', 32)

resource uami 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: uamiName
  location: location
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

// MANDATORY: AcrPull role assignment for the user-assigned managed identity (define BEFORE any container apps)
resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, uami.id, 'AcrPull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: uami.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

resource cae 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: caeName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// Tags required for compute resources
var computeTags = {
  'azd-service-name': 'fabdemcp'
}

resource ca 'Microsoft.App/containerApps@2023-05-01' = {
  name: caName
  location: location
  tags: computeTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${uami.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: cae.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        corsPolicy: {
          allowedOrigins: [
            '*'
          ]
          allowedMethods: [
            'GET'
            'POST'
            'OPTIONS'
          ]
          allowedHeaders: [
            '*'
          ]
        }
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: uami.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'fabdemcp'
          // Mandatory placeholder; azd deploy updates to the built image.
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          env: [
            {
              name: 'FASTMCP_HOST'
              value: '0.0.0.0'
            }
            {
              name: 'FASTMCP_PORT'
              value: '8000'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}

@description('Resource group id')
output RESOURCE_GROUP_ID string = resourceGroup().id

@description('Container Registry endpoint (loginServer)')
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = acr.properties.loginServer

@description('Container App FQDN')
output CONTAINER_APP_FQDN string = ca.properties.configuration.ingress.fqdn
