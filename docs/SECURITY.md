# Security Best Practices

## Authentication

1. **Use Managed Identity (Future)**: Once available, avoid PAT tokens in production
2. **Rotate PATs Regularly**: Set reasonable expiration periods (90 days recommended, max 730)
3. **Secure PAT Storage**: Never commit PATs to source control
4. **Use Existing PAT Option**: For production, manage PATs centrally and pass via `--databricks-pat`

## Access Control

1. **Least Privilege**: Grant only necessary permissions to the managed identity
2. **RBAC Reviews**: Periodically review and audit role assignments
3. **Scope Restrictions**: Limit connection access to specific agents/projects

## Network Security

1. **Private Endpoints**: Use private endpoints for Databricks when possible
2. **Network Policies**: Configure network access restrictions
3. **VNet Integration**: Deploy resources within secure virtual networks

## Monitoring & Auditing

1. **Enable Diagnostic Logs**: Configure logging on both AI Foundry and Databricks
2. **Monitor API Calls**: Track agent API usage and patterns
3. **Alert on Anomalies**: Set up alerts for unusual access patterns
4. **Audit Trail**: Maintain audit logs for compliance requirements

## Secrets Management

1. **Use Databricks Secrets API**: Store sensitive data in Databricks secret scopes
2. **Avoid Hardcoding**: Never hardcode credentials in notebooks or code
3. **Scope Access Control**: Restrict secret scope access to authorized users/groups
4. **Secret Rotation**: Implement regular secret rotation policies

## Compliance

1. **Data Residency**: Ensure resources are in compliant regions
2. **Encryption**: Enable encryption at rest and in transit
3. **Access Reviews**: Conduct regular access reviews
4. **Documentation**: Maintain documentation of security controls

## References

- [Azure Databricks Security Best Practices](https://learn.microsoft.com/azure/databricks/security/)
- [Managed Identity Overview](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)
- [Azure AI Foundry Security](https://learn.microsoft.com/azure/ai-studio/concepts/security)
