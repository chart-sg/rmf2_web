import * as RomiCore from '@osrf/romi-js-core-interfaces';
import { Meta, Story } from '@storybook/react';
import React from 'react';
import { LiftMarker, LiftMarkerProps } from '../lib';
import { makeLift, makeLiftState } from '../tests/lifts/test-utils';

export default {
  title: 'Lift Markers',
  component: LiftMarker,
} as Meta;

function makeStory(
  lift: RomiCore.Lift,
  liftState?: RomiCore.LiftState,
  variant?: LiftMarkerProps['variant'],
): Story {
  return (args) => (
    <svg viewBox="-2 -2 4 4" width={400} height={400}>
      <LiftMarker lift={lift} liftState={liftState} variant={variant} {...args} />
    </svg>
  );
}

export const Basic = makeStory(makeLift(), makeLiftState());

export const UnknownState = makeStory(makeLift(), undefined, 'unknown');

export const Rotated = makeStory(
  makeLift({
    ref_yaw: Math.PI / 4,
    doors: [
      {
        name: 'door',
        door_type: RomiCore.Door.DOOR_TYPE_DOUBLE_TELESCOPE,
        motion_direction: 1,
        motion_range: Math.PI / 2,
        v1_x: -1.414,
        v1_y: 0,
        v2_x: 0,
        v2_y: -1.414,
      },
    ],
  }),
  makeLiftState(),
);

export const LongLongLift = makeStory(
  makeLift({
    width: 4,
    depth: 2,
    doors: [
      {
        name: 'door',
        door_type: RomiCore.Door.DOOR_TYPE_DOUBLE_TELESCOPE,
        motion_direction: 1,
        motion_range: Math.PI / 2,
        v1_x: -2,
        v1_y: -1,
        v2_x: 2,
        v2_y: -1,
      },
    ],
  }),
  makeLiftState(),
);