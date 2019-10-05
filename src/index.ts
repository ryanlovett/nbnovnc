// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';
import { PageConfig } from '@jupyterlab/coreutils';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { Menu } from '@phosphor/widgets';

export namespace CommandIDs {
  export const controlPanel: string = 'novnc:control-panel';
}

const noVncExtension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-novnc',
  autoStart: true,
  requires: [ICommandPalette, IMainMenu],
  activate: activate,
};

function activate(
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  mainMenu: IMainMenu,

): void {

  const vncBase = PageConfig.getBaseUrl().replace('http://', '').replace('https://', '');
  const vncSuffix = 'novnc/vnc.html?resize=remote&autoconnect=true';
  const vncURL = PageConfig.getBaseUrl() + '/novnc/?host=' + vncBase + vncSuffix;
  if (!vncURL) {
    console.log('jupyterlab-vnc: No configuration found.');
    return;
  }

  const category = 'VNC';
  const { commands } = app;
  commands.addCommand(CommandIDs.controlPanel, {
    label: 'Go To VNC',
    caption: 'Open the VNC window in a new browser tab',
    execute: () => {
      window.open(vncURL, '_blank');
    },
  });

  // Add commands and menu itmes.
  const menu = new Menu({ commands });
  menu.title.label = category;
  [CommandIDs.controlPanel].forEach((command) => {
    palette.addItem({ command, category });
    menu.addItem({ command });
  });
  mainMenu.addMenu(menu, { rank: 100 });
}

export default noVncExtension;
