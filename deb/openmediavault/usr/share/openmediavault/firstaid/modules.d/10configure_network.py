#!/usr/bin/env python3
#
# This file is part of OpenMediaVault.
#
# @license   http://www.gnu.org/licenses/gpl.html GPL Version 3
# @author    Volker Theile <volker.theile@openmediavault.org>
# @copyright Copyright (c) 2009-2016 Volker Theile
#
# OpenMediaVault is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# OpenMediaVault is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenMediaVault. If not, see <http://www.gnu.org/licenses/>.
import sys
import dialog
import pyudev
import ipaddress
import re
import natsort
import openmediavault as omv

class Module(omv.firstaid.IModule):
	@property
	def description(self):
		return "Configure network interface"

	def execute(self):
		# Default values.
		address = None
		netmask = None
		gateway = None
		method = "dhcp"
		address6 = ""
		method6 = "manual"
		netmask6 = 64
		gateway6 = ""
		wol = False
		dns_nameservers = None
		wpa_ssid = None
		wpa_psk = None
		rpc_method = "setEthernetIface"
		rpc_params = {}
		# Get the network interface device.
		devices = []
		context = pyudev.Context()
		for device in context.list_devices(subsystem="net"):
			# Skip unwanted network interface devices.
			if device.sys_name in ("lo"):
				continue
			if device.device_type and device.device_type in ("bond"):
				continue
			# Append the network interface name for later use.
			devices.append(device.sys_name)
		devices = natsort.humansorted(devices)
		choices = []
		for idx, sys_name in enumerate(devices):
			device = pyudev.Device.from_name(context, "net", sys_name)
			for id in [ "ID_MODEL_FROM_DATABASE", "ID_VENDOR_FROM_DATABASE" ]:
				if not id in device:
					continue
				choices.append([ sys_name, omv.string.truncate(
					device[id], 50) ])
				break
		d = dialog.Dialog(dialog="dialog")
		(code, tag) = d.menu("Please select a network interface. Note, the " \
			"existing network interface configuration will be deleted.",
			backtitle=self.description, clear=True,
			height=14, width=70, menu_height=6, choices=choices)
		if code in (d.CANCEL, d.ESC):
			return 0
		device_name = tag
		# Use DHCP?
		code = d.yesno("Do you want to use DHCPv4 for this interface?",
			backtitle=self.description,
			height=5, width=49)
		if code == d.ESC:
			return 0
		if code != d.OK:
			method = "static"
			# Get the static IPv4 address.
			while not address:
				(code, address) = d.inputbox(
					"Please enter the IPv4 address.",
					backtitle=self.description,
					clear=True, height=8, width=60, init="")
				if code != d.OK:
					return 0
				if not address:
					d.msgbox("The field must not be empty.",
						backtitle=self.description,
						height=5, width=32)
					continue
				try:
					ipaddress.ip_address(address)
				except Exception as e:
					address = None
					d.msgbox("Please enter a valid IPv4 address.",
						backtitle=self.description,
						height=5, width=38)
					continue
			# Get the IPv4 netmask.
			while not netmask:
				(code, netmask) = d.inputbox(
					"Please enter the IPv4 netmask.",
					backtitle=self.description,
					clear=True, height=8, width=60, init="")
				if code != d.OK:
					return 0
				if not netmask:
					d.msgbox("The field must not be empty.",
						backtitle=self.description,
						height=5, width=32)
					continue
				try:
					ipaddress.ip_address(netmask)
				except:
					netmask = None
					d.msgbox("Please enter a valid netmask.",
						backtitle=self.description,
						height=5, width=33)
					continue
			# Get default IPv4 gateway.
			while not gateway:
				(code, gateway) = d.inputbox(
					"Please enter the default IPv4 gateway.",
					backtitle=self.description,
					clear=True, height=8, width=60, init="")
				if code != d.OK:
					return 0
				try:
					ipaddress.ip_address(gateway)
				except:
					gateway = None
					d.msgbox("Please enter a valid gateway.",
						backtitle=self.description,
						height=5, width=33)
					continue
		# Use IPv6?
		code = d.yesno("Do you want to configure IPv6 for this interface?",
			backtitle=self.description,
			height=5, width=53, defaultno=True)
		if code == d.ESC:
			return 0
		if code == d.OK:
			# Use stateful address autoconfiguration (DHCPv6)?
			code = d.yesno("Do you want to enable stateful address " \
				"autoconfiguration (DHCPv6)?",
				backtitle=self.description,
				height=6, width=42)
			if code == d.ESC:
				return 0
			if code == d.OK:
				method6 = "dhcp"
			else:
				# Use stateless address autoconfiguration (SLAAC)?
				code = d.yesno("Do you want to enable stateless address " \
					"autoconfiguration (SLAAC)?",
					backtitle=self.description,
					height=6, width=42)
				if code == d.ESC:
					return 0
				if code == d.OK:
					method6 = "auto"
				else:
					method6 = "static"
				# Get static IPv6 address.
				address6 = None
				while not address6:
					(code, address6) = d.inputbox(
						"Please enter the IPv6 address.",
						backtitle=self.description,
						clear=True, height=8, width=60, init="")
					if code != d.OK:
						return 0
					if not address6:
						d.msgbox("The field must not be empty.",
							backtitle=self.description,
							height=5, width=32)
						continue
					try:
						ipaddress.ip_address(address6)
					except:
						address6 = None
						d.msgbox("Please enter a valid IPv6 address.",
							backtitle=self.description,
							height=5, width=38)
						continue
				# Get the prefix length.
				netmask6 = None
				while not netmask6:
					(code, netmask6) = d.inputbox(
						"Please enter the IPv6 prefix length.",
						backtitle=self.description,
						clear=True, height=8, width=64, init="64")
					if code != d.OK:
						return 0
					if not netmask6:
						d.msgbox("The field must not be empty.",
							backtitle=self.description,
							height=5, width=32)
						continue
					try:
						ipaddress.ip_address(netmask6)
					except:
						netmask6 = None
						d.msgbox("Please enter a valid netmask.",
							backtitle=self.description,
							height=5, width=33)
						continue
				# Get default IPv6 gateway.
				gateway6 = None
				while not gateway6:
					(code, gateway6) = d.inputbox(
						"Please enter the default IPv6 gateway.",
						backtitle=self.description,
						clear=True, height=8, width=60, init="")
					if code != d.OK:
						return 0
					try:
						ipaddress.ip_address(gateway6)
					except:
						gateway6 = None
						d.msgbox("Please enter a valid gateway.",
							backtitle=self.description,
							height=5, width=33)
						continue
		# Get the DNS name servers. Note, only one IP address is
		# supported here.
		if method == "static" or method6 == "static":
			while True:
				(code, dns_nameservers) = d.inputbox(
					"Please enter the DNS name server. If you don't want " \
					"to use any name server, just leave this field blank.",
					backtitle=self.description,
					clear=True, height=8, width=60, init="")
				if code != d.OK:
					return 0
				if not dns_nameservers:
					break
				try:
					ipaddress.ip_address(dns_nameservers)
					break
				except:
					dns_nameservers = None
					d.msgbox("Please enter a valid IP address.",
						backtitle=self.description,
						height=5, width=30)
		# Enable WOL?
		code = d.yesno("Do you want to enable WOL for this interface?",
			backtitle=self.description,
			height=5, width=50, defaultno=True)
		if code == d.ESC:
			return 0
		if code == d.OK:
			wol = True
		# Set the default RPC parameters.
		rpc_params.update({
			"uuid": omv.getenv("OMV_CONFIGOBJECT_NEW_UUID"),
			"devicename": device_name,
			"method": method,
			"address": address,
			"netmask": netmask,
			"gateway": gateway,
			"method6": method6,
			"address6": address6,
			"netmask6": netmask6,
			"gateway6": gateway6,
			"dnsnameservers": dns_nameservers,
			"dnssearch": "",
			"mtu": 0,
			"wol": wol,
			"options": "",
			"comment": "",
		})
		# Do we process a wireless network interface?
		if re.match(r"^wlan[0-9]+$", device_name):
			rpc_method = "setWirelessIface"
			# Get the SSID.
			while not wpa_ssid:
				(code, wpa_ssid) = d.inputbox(
					"Please enter the name of the wireless network (SSID).",
					backtitle=self.description,
					clear=True, height=8, width=60, init="")
				if code != d.OK:
					return 0
				if not wpa_ssid:
					d.msgbox("The field must not be empty.",
						backtitle=self.description,
						height=5, width=32)
			rpc_params["wpassid"] = wpa_ssid
			# Get the pre-shared key.
			while not wpa_psk:
				(code, wpa_psk) = d.inputbox(
					"Please enter the pre-shared key (PSK).",
					backtitle=self.description,
					clear=True, height=8, width=45, init="")
				if code != d.OK:
					return 0
				if not wpa_psk:
					d.msgbox("The field must not be empty.",
						backtitle=self.description,
						height=5, width=32)
			rpc_params["wpapsk"] = wpa_psk
		# Update the interface configuration.
		print("Configuring network interface. Please wait ...")
		# Delete all existing network interface configuration objects.
		interfaces = omv.rpc.call("Network", "enumerateConfiguredDevices")
		for interface in interfaces:
			omv.rpc.call("Network", "deleteInterface", {
				"uuid": interface["uuid"] })
		# Insert a new network interface configuration object.
		omv.rpc.call("Network", rpc_method, rpc_params)
		omv.rpc.call("Config", "applyChanges", { "modules": [],
			"force": False })
		print("The network interface configuration was successfully changed.")
		return 0

if __name__ == "__main__":
	module = Module();
	sys.exit(module.execute())