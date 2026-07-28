// resources.bicep — the actual AI-901 demo resources (resource-group scope).
// One Microsoft Foundry (AIServices) account covers chat, vision, image gen,
// Speech, and Content Understanding; a Foundry project hosts agents.

@description('Location for all resources.')
param location string

@description('Tags applied to every resource.')
param tags object

@description('Deterministic token used to build unique resource names.')
param resourceToken string

@description('Object ID of the signed-in user, for keyless RBAC.')
param principalId string

@description('Type of the principal receiving RBAC roles.')
param principalType string

@description('Disable shared-key (local) auth so only Entra ID credentials work. Keep true unless you need the preview key-auth Speech MCP tool.')
param disableLocalAuth bool

param chatModelName string
param chatModelVersion string
param chatCapacity int
param imageModelName string
param imageModelVersion string
param embeddingModelName string
param embeddingModelVersion string
param embeddingCapacity int
param realtimeModelName string
param realtimeModelVersion string
param realtimeCapacity int

var aiServicesName = 'ais${resourceToken}'
var projectName = 'proj${resourceToken}'
var chatDeploymentName = 'gpt-5.1'
var imageDeploymentName = 'gpt-image-1'
var embeddingDeploymentName = 'text-embedding-3-small'
var realtimeDeploymentName = 'gpt-realtime'

// Microsoft Foundry account (AIServices) with project management enabled.
resource aiServices 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: aiServicesName
  location: location
  tags: tags
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    // Required so the account can host Foundry projects (agents).
    allowProjectManagement: true
    // Required for keyless (Entra ID) access via a stable *.services.ai.azure.com domain.
    customSubDomainName: aiServicesName
    // Entra-only auth by default; every demo uses DefaultAzureCredential. Set the
    // disableLocalAuth param to false only for the preview key-auth Speech MCP tool.
    disableLocalAuth: disableLocalAuth
    // DEMO ONLY: the account is reachable from any network so learners can run the
    // scripts from their own machines. For anything beyond a classroom, restrict this
    // with networkAcls / a private endpoint.
    publicNetworkAccess: 'Enabled'
  }
}

// Foundry project — the endpoint the Foundry SDK / agents connect to.
resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: aiServices
  name: projectName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'AI-901 Demos'
    description: 'Project for the AI-901 fundamentals demos.'
  }
}

// Model deployments. Cognitive Services rejects parallel deployment creation,
// so they are chained with dependsOn to run one at a time.
resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: aiServices
  name: chatDeploymentName
  sku: { name: 'GlobalStandard', capacity: chatCapacity }
  properties: {
    model: { format: 'OpenAI', name: chatModelName, version: chatModelVersion }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
}

resource imageDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: aiServices
  name: imageDeploymentName
  sku: { name: 'GlobalStandard', capacity: 1 }
  properties: {
    model: { format: 'OpenAI', name: imageModelName, version: imageModelVersion }
  }
  dependsOn: [ chatDeployment ]
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: aiServices
  name: embeddingDeploymentName
  sku: { name: 'GlobalStandard', capacity: embeddingCapacity }
  properties: {
    model: { format: 'OpenAI', name: embeddingModelName, version: embeddingModelVersion }
  }
  dependsOn: [ imageDeployment ]
}

// Realtime model for the OPTIONAL Voice Live demo (Module 4, Part C).
// Real-time speech-to-speech needs a realtime-capable model, not gpt-5.1.
resource realtimeDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: aiServices
  name: realtimeDeploymentName
  sku: { name: 'GlobalStandard', capacity: realtimeCapacity }
  properties: {
    model: { format: 'OpenAI', name: realtimeModelName, version: realtimeModelVersion }
  }
  dependsOn: [ embeddingDeployment ]
}

// Keyless RBAC for the signed-in user. Covers OpenAI models, Speech,
// Content Understanding, and Foundry agents.
var roleDefinitionIds = [
  '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
  'a97b65f3-24c7-4388-baec-2e87135dc908' // Cognitive Services User
  '64702f94-c441-49e6-a78b-ef80e0188fee' // Azure AI Developer
  '53ca6127-db72-4b80-b1b0-d745d6d5456d' // Azure AI User
]

resource roleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for roleId in roleDefinitionIds: if (!empty(principalId)) {
    name: guid(aiServices.id, principalId, roleId)
    scope: aiServices
    properties: {
      roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleId)
      principalId: principalId
      principalType: principalType
    }
  }
]

output FOUNDRY_PROJECT_ENDPOINT string = 'https://${aiServicesName}.services.ai.azure.com/api/projects/${projectName}'
output CONTENT_UNDERSTANDING_ENDPOINT string = 'https://${aiServicesName}.services.ai.azure.com/'
// Azure AI Language APIs (e.g. PII detection) use the multi-service Cognitive
// Services endpoint on the same account.
output LANGUAGE_ENDPOINT string = 'https://${aiServicesName}.cognitiveservices.azure.com/'
// Full ARM resource ID of the account — needed for keyless (AAD) Speech auth.
output SPEECH_RESOURCE_ID string = aiServices.id
output CHAT_DEPLOYMENT string = chatDeploymentName
output MULTIMODAL_DEPLOYMENT string = chatDeploymentName
output IMAGE_DEPLOYMENT string = imageDeploymentName
output EMBEDDING_DEPLOYMENT string = embeddingDeploymentName
output VOICE_LIVE_MODEL string = realtimeDeploymentName
