# n8n Workflow JSON Structure Research

## Overview
This document outlines the research findings regarding n8n's workflow JSON structure, which is crucial for the Make-to-n8n converter implementation.

## Core Components

### 1. Workflow Metadata
- `id`: Unique identifier for the workflow
- `name`: Human-readable workflow name
- `active`: Boolean indicating if workflow is active
- `settings`: Global workflow settings including:
  - `executionOrder`: Version of execution order (e.g., "v1")
  - `saveExecutionProgress`: Whether to save execution progress
  - `saveManualExecutions`: Whether to save manual execution data
  - `timezone`: Workflow timezone setting
- `versionId`: Version number of the workflow
- `createdAt`: Timestamp of creation
- `updatedAt`: Timestamp of last update

### 2. Node Structure
Each node in an n8n workflow contains:
- `id`: Unique node identifier
- `name`: Display name of the node
- `type`: Node type identifier (e.g., "n8n-nodes-base.httpRequest")
- `typeVersion`: Version of the node type
- `position`: [x, y] coordinates for UI placement
- `parameters`: Node-specific configuration
- `disabled`: Boolean indicating if node is disabled

### 3. Connection Structure
- Connections are stored in a dedicated object
- Each connection defines:
  - Source node and output
  - Target node and input
  - Data flow routing rules
  - Error handling paths

### 4. Additional Components
- `tags`: Workflow categorization tags
- `pinData`: Pinned data for testing
- `staticData`: Persistent data storage
- `triggerCount`: Number of trigger nodes
- `nodes`: Array of all workflow nodes
- `connections`: Object defining node connections

## Best Practices

### 1. Node Configuration
- Use unique IDs for each node
- Maintain consistent type versions
- Include all required parameters
- Handle optional parameters appropriately

### 2. Connection Management
- Ensure valid source and target nodes
- Define clear data paths
- Include error handling routes
- Maintain connection integrity

### 3. Workflow Settings
- Set appropriate timezone
- Configure execution settings
- Enable necessary features
- Maintain version control

## Implementation Considerations

### 1. Data Types
- Use correct data types for parameters
- Handle type conversions properly
- Validate data formats

### 2. Error Handling
- Include error routing
- Define fallback paths
- Handle edge cases

### 3. Version Compatibility
- Check node type versions
- Ensure workflow version compatibility
- Handle deprecated features

## Validation Requirements

### 1. Schema Validation
- Validate against n8n schema
- Check required fields
- Verify data types
- Ensure structural integrity

### 2. Connection Validation
- Verify node references
- Check connection validity
- Validate routing rules

### 3. Parameter Validation
- Check required parameters
- Validate parameter formats
- Verify parameter compatibility

## Notes for Conversion
- Ensure unique ID generation
- Map node types correctly
- Preserve connection logic
- Handle platform-specific features
- Maintain data integrity
- Consider error handling differences
- Validate final output 