import { Settings } from '@/components/settings/settings';
import { FlowTabContent } from '@/components/tabs/flow-tab-content';
import { BacktestHistory } from '@/components/backtest-history/backtest-history';
import { Flow } from '@/types/flow';
import { ReactNode, createElement } from 'react';

export interface TabData {
  type: 'flow' | 'settings' | 'backtest-history';
  title: string;
  flow?: Flow;
  metadata?: Record<string, any>;
}

export class TabService {
  static createTabContent(tabData: TabData): ReactNode {
    switch (tabData.type) {
      case 'flow':
        if (!tabData.flow) {
          throw new Error('Flow tab requires flow data');
        }
        return createElement(FlowTabContent, { flow: tabData.flow });

      case 'settings':
        return createElement(Settings);

      case 'backtest-history':
        return createElement(BacktestHistory);

      default:
        throw new Error(`Unsupported tab type: ${tabData.type}`);
    }
  }

  static createFlowTab(flow: Flow): TabData & { content: ReactNode } {
    return {
      type: 'flow',
      title: flow.name,
      flow: flow,
      content: TabService.createTabContent({ type: 'flow', title: flow.name, flow }),
    };
  }

  static createSettingsTab(): TabData & { content: ReactNode } {
    return {
      type: 'settings',
      title: 'Settings',
      content: TabService.createTabContent({ type: 'settings', title: 'Settings' }),
    };
  }

  static createBacktestHistoryTab(): TabData & { content: ReactNode } {
    return {
      type: 'backtest-history',
      title: 'Backtest History',
      content: TabService.createTabContent({ type: 'backtest-history', title: 'Backtest History' }),
    };
  }

  // Restore tab content for persisted tabs (used when loading from localStorage)
  static restoreTabContent(tabData: TabData): ReactNode {
    return TabService.createTabContent(tabData);
  }

  // Helper method to restore a complete tab from saved data
  static restoreTab(savedTab: TabData): TabData & { content: ReactNode } {
    switch (savedTab.type) {
      case 'flow':
        if (!savedTab.flow) {
          throw new Error('Flow tab requires flow data for restoration');
        }
        return TabService.createFlowTab(savedTab.flow);

      case 'settings':
        return TabService.createSettingsTab();

      case 'backtest-history':
        return TabService.createBacktestHistoryTab();

      default:
        throw new Error(`Cannot restore unsupported tab type: ${savedTab.type}`);
    }
  }
} 