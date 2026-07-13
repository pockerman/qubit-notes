# qubit-note: Terraform | Output Values

Output values in Terraform are a way to retrieve and display important information from your Terraform deployments after the infrastructure has been applied. They provide a clean, programmatic method to access details such as IP addresses, connection strings, or resource IDs.

Here are the key features of output values:

Immediate Feedback: Once your Terraform run has completed, outputs appear in the command line interface. This immediate feedback helps you verify your deployment and access essential information quickly.

Stored in State File: Outputs are saved in the Terraform state file, allowing you to retrieve the information anytime without rerunning your configuration. This is especially useful when working with existing infrastructure.

Sensitive Values: For security considerations, outputs containing sensitive information can be marked as sensitive. This prevents accidental exposure of confidential data in logs or output displays.

Modularity: Outputs are crucial when using Terraform modules, as they allow data to be passed between modules, promoting a more modular and reusable infrastructure code.

Display Example: An output might define an IP address of a service deployed. For instance:

Code
output "instance_public_ip" {
  description = "Public IP address of the web server"
  value       = aws_instance.my_instance.public_ip
}
This output block retrieves the public IP of a web server after deployment.

By utilizing output values, you can streamline your infrastructure management and enhance automation within your deployments.