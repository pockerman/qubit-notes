# qubit-note: RaspeberryPi Series | Connect to RaspberryPi Using SSH

## Overview

In a previous note, <a href="2025-12-30-connect-raspberrypi-connect.md">Connect to RaspberryPi Using Raspberry Pi Connect</a>, we saw how to connect to connect to Raspberry Pi using
Pi Connect. In this note we will see how to connect to Raspberry Pi using SSH. The material we will discuss here can be found in <a href="https://raspberrypi-guide.github.io/networking/connecting-via-ssh">Connecting to your Raspberry Pi via SSH</a>

## Connect to RaspberryPi using ssh

Secure Shell (SSH) enables you to access the command line of a Raspberry Pi from another computer or device on the same network. This is very handy for quickly installing software or editing configuration files. SSH is pre-installed on Linux, Mac and some Windows operating systems and can also be installed on mobile devices. SSH does not provide any visual access to the Raspberry Pi Desktop. If this is needed, I recommend to use VNC.

Enable SSH on the Raspberry Pi
By default, SSH is disabled on the Raspberry Pi. It is however very easy to enable it, both using the Desktop and via the terminal. To enable SSH via the Desktop, go to the start menu > Preferences > Raspberry Pi Configuration.


Connecting via SSH
Now SSH is enabled, we need to know the hostname of the Raspberry Pi or use its IP address to connect to it. To know the ip address, on your Raspbery Pi type in:

```
hostname -I
```

Now to connect, on the host computer open a terminal window and type in

```
ssh [username]@[hostname].local
```

or

```
ssh [username]@[ip address]
```

Passwordless SSH
When using SSH, each time you connect you will be asked for the password of your Raspberry Pi. In some cases it may be preferable to access your Raspberry Pi from another computer without a password, such as to (automatically) send files using rsync (follow the guide here). To enable password-less access with SSH you will need to generate an SSH key. To do so, open a terminal window and enter:

ssh-keygen
Now click Enter twice to generate and store the unique key in the default location and with the default passphrase. The private and public keys will now be stored in ~/.ssh.

Next we need to copy the public key to your Raspberry Pi. To do so, simply enter:

```
ssh-copy-id [username]@[ip address]
```

Authenticate this step with your password and you are done. To verify the SSH key was successfully copied to the remote host, SSH to the Raspberry Pi from the host device or vice versa. No password should be required if the key was copied successfully.


---
**Remark Shutting down your Raspberry Pi**

When you have finished your session with the Pi, shut it down with 
```
sudo poweroff.
```

Wait for the green light activity to stop; SSH will detect that it has disconnected. You can then
safely disconnect the power.

---


## Summary

## References

1. <a href="https://raspberrypi-guide.github.io/networking/connecting-via-ssh">Connecting to your Raspberry Pi via SSH</a>