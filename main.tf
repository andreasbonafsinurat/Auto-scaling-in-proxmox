terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "~> 2.9.14"
    }
  }
}

provider "proxmox" {
  pm_api_url      = "https://192.168.1.100:8006/api2/json"
  pm_user         = "root@pam"
  pm_password     = "clouddata"
  pm_tls_insecure = true
}

variable "vm_count" {
  description = "Jumlah VM yang akan dibuat"
  type        = number
  default     = 1
}

resource "proxmox_vm_qemu" "vm" {
  count       = var.vm_count
  name        = "scaling-vm-${count.index + 1}"
  target_node = "comnetscloud"  # Ganti dengan nama node Proxmox Anda
  clone       = "Template"  # Ganti dengan nama template VM Anda

  disk {
    size = "25G"
    type = "scsi"
    storage = "local-lvm"
  }

  network {
    model  = "virtio"
    bridge = "vmbr0"
  }

  provisioner "local-exec" {
    command = "echo ${self.default_ipv4_address} >> ~/vm_ips.txt"
  }
}

output "vm_ips" {
  value = [for vm in proxmox_vm_qemu.vm : vm.default_ipv4_address]
}
