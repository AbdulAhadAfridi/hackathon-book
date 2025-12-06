import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Foundations of Humanoid Robotics',
      items: [
        'foundations/introduction',
        'foundations/history-evolution',
        'foundations/robot-anatomy',
      ],
    },
    {
      type: 'category',
      label: 'Mechanical & Hardware Systems',
      items: [
        'mechanics/sensors',
        'mechanics/actuators-motors',
        'mechanics/kinematics',
      ],
    },
    {
      type: 'category',
      label: 'Embedded Systems & Control',
      items: [
        'embedded-control/microcontrollers-os',
        'embedded-control/control-loops',
        'embedded-control/power-management',
      ],
    },
    {
      type: 'category',
      label: 'AI for Humanoid Robotics',
      items: [
        'ai-systems/computer-vision-perception',
        'ai-systems/motion-planning-algorithms',
        'ai-systems/reinforcement-learning',
      ],
    },
    {
      type: 'category',
      label: 'Integration & Behaviour',
      items: [
        'behavior-integration/sensor-fusion',
        'behavior-integration/real-time-decision-systems',
        'behavior-integration/human-robot-interaction',
      ],
    },
    {
      type: 'category',
      label: 'Tools, Simulation & Testing',
      items: [
        'simulation-testing/simulation-platforms',
        'simulation-testing/dataset-generation',
        'simulation-testing/safety-testing-debugging',
      ],
    },
    {
      type: 'category',
      label: 'Applications & Future',
      items: [
        'applications/healthcare-humanoids',
        'applications/industrial-service-robots',
        'applications/future-trends-challenges',
      ],
    },
  ],
};

export default sidebars;
