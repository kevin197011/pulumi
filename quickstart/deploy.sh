# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

mkdir -p $(pwd)/state

export PULUMI_BACKEND_URL=file://$(pwd)/state
export PULUMI_CONFIG_PASSPHRASE="123456"
pulumi login $PULUMI_BACKEND_URL

pulumi up --yes --stack dev
if [ $? -ne 0 ]; then
    echo "Pulumi deployment failed. Please check the output for errors."
    exit 1
fi
echo "Pulumi deployment completed successfully."
pulumi stack output --json > $(pwd)/state/outputs.json
echo "Outputs saved to $(pwd)/state/outputs.json"
echo "Deployment completed successfully. You can now access your resources."
echo "To destroy the resources, run 'pulumi destroy --yes --stack dev' in the same directory."
# echo "To view the state, run 'pulumi stack' in the same directory."
# echo "To view the outputs, run 'pulumi stack output' in the same directory."
# echo "To view the logs, run 'pulumi logs --follow' in the same directory."
# echo "To view the resources, run 'pulumi stack resources' in the same directory."
# echo "To view the configuration, run 'pulumi config' in the same directory."
# echo "To view the stack history, run 'pulumi stack history' in the same directory."
# echo "To view the stack info, run 'pulumi stack output --json' in the same directory."
# echo "To view the stack diff, run 'pulumi stack diff' in the same directory."
# echo "To view the stack preview, run 'pulumi preview' in the same directory."
# echo "To view the stack logs, run 'pulumi logs' in the same directory."
