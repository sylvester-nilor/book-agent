# Book Agent - Proactive Knowledge Agent

A conversational AI agent that proactively enriches natural conversations with relevant insights from a knowledge base. The agent engages in genuine dialogue while intelligently searching for and weaving in relevant knowledge when it could add value to the conversation.

## Deployment

Deploy the service using the `deploy.sh` script:

```bash
# Deploy with image rebuild
./deploy.sh -b t

# Deploy without image rebuild  
./deploy.sh -b f

# Plan changes without applying (dry run)
./deploy.sh -b t -p
./deploy.sh -b f --plan
```

# Enhancements

1. TBD