/**
 * This file is part of OpenMediaVault.
 *
 * @license   http://www.gnu.org/licenses/gpl.html GPL Version 3
 * @author    Volker Theile <volker.theile@openmediavault.org>
 * @copyright Copyright (c) 2009-2018 Volker Theile
 *
 * OpenMediaVault is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * any later version.
 *
 * OpenMediaVault is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with OpenMediaVault. If not, see <http://www.gnu.org/licenses/>.
 */
// require("js/omv/WorkspaceManager.js")
// require("js/omv/workspace/panel/Textarea.js")

/**
 * @class OMV.module.admin.diagnostic.system.Top
 * @derived OMV.workspace.panel.Textarea
 */
Ext.define("OMV.module.admin.diagnostic.system.Top", {
	extend: "OMV.workspace.panel.Textarea",

	rpcService: "System",
	rpcMethod: "getTopInfo"
});

OMV.WorkspaceManager.registerPanel({
	id: "top",
	path: "/diagnostic/system",
	text: _("Processes"),
	position: 20,
	className: "OMV.module.admin.diagnostic.system.Top"
});
