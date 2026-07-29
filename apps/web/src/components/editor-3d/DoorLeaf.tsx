'use client';

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { MeshStandardMaterial } from 'three';
import { useFloorPlanStore } from '@/stores/floorPlanStore';

interface DoorLeafProps {
  /** Center of the opening (world space). */
  position: [number, number, number];
  /** Wall yaw (radians). The leaf is built in the wall's local frame. */
  rotationY: number;
  /** Door leaf width (mm), equals the opening width. */
  width: number;
  /** Door leaf height (mm), equals the opening height. */
  height: number;
  /** Sill height (mm) — bottom of the leaf. */
  sillHeight: number;
  /** Hinge side: 'left' hinge is at the -X edge of the opening (in wall-local
   * frame), 'right' at the +X edge. Default 'left'. */
  hingeSide: 'left' | 'right';
  /** Which way the door opens (rotation sign). Default 'inward'. */
  swingDirection: 'inward' | 'outward';
  /** Opening id — used to read/toggle open state from the store. */
  openingId: string;
  /** Leaf color. */
  color: string;
}

const ANIM_SPEED = 6; // higher = snappier; lerp factor per second (scaled by dt)

/**
 * A swingable door panel. Click to toggle open/close; the leaf smoothly
 * rotates around its hinge (Y axis) between closed (0deg) and open (~95deg).
 *
 * Geometry strategy: the leaf box is built centered on the opening, then the
 * whole thing is wrapped in a pivot <group> that sits at the hinge edge. The
 * pivot's Y rotation is what animates — everything else (wall yaw, position,
 * sill height) is applied by outer groups so the pivot only ever changes the
 * swing angle.
 */
export function DoorLeaf({
  position,
  rotationY,
  width,
  height,
  sillHeight,
  hingeSide,
  swingDirection,
  openingId,
  color,
}: DoorLeafProps) {
  const pivotRef = useRef<THREE.Group>(null);
  const isOpen = useFloorPlanStore((s) => s.doorOpenState[openingId] ?? false);
  const toggleDoor = useFloorPlanStore((s) => s.toggleDoor);

  // Target angle (radians). Closed = 0. Open ~95deg, sign depends on hinge
  // side + swing direction so the door always opens into the correct room.
  const hingeSign = hingeSide === 'left' ? 1 : -1;
  const swingSign = swingDirection === 'inward' ? 1 : -1;
  const targetAngle = isOpen ? hingeSign * swingSign * (95 * (Math.PI / 180)) : 0;

  useFrame((_, delta) => {
    const grp = pivotRef.current;
    if (!grp) return;
    // Frame-rate independent exponential lerp toward the target angle.
    const current = grp.rotation.y;
    const t = 1 - Math.exp(-ANIM_SPEED * Math.min(delta, 0.1));
    grp.rotation.y = current + (targetAngle - current) * t;
  });

  const material = useMemo(
    () => new MeshStandardMaterial({ color, roughness: 0.55, metalness: 0.15 }),
    [color],
  );

  // Leaf local geometry: a thin panel. Offset so its inner edge aligns with
  // the hinge; the box is centered then shifted by half-width toward the
  // hinge (local -X for a left hinge, +X for a right hinge).
  const offset = hingeSide === 'left' ? -width / 2 : width / 2;

  // A small doorknob offset on the free edge for a touch of realism.
  const knobX = hingeSide === 'left' ? width / 2 - 15 : -width / 2 + 15;

  return (
    // Outer group: world position + wall yaw.
    <group position={position} rotation={[0, rotationY, 0]}>
      {/* Pivot group at the hinge edge — this is the only thing that rotates. */}
      <group ref={pivotRef} position={[offset, 0, 0]}>
        {/* Leaf body. */}
        <mesh
          geometry={undefined}
          material={material}
          position={[0, sillHeight + height / 2, 0]}
          onClick={(e) => {
            e.stopPropagation();
            toggleDoor(openingId);
          }}
          castShadow
        >
          <boxGeometry args={[width, height, 4]} />
        </mesh>
        {/* Doorknob. */}
        <mesh position={[knobX, sillHeight + height / 2, 6]} onClick={(e) => {
          e.stopPropagation();
          toggleDoor(openingId);
        }}>
          <sphereGeometry args={[5, 12, 12]} />
          <meshStandardMaterial color="#b45309" roughness={0.3} metalness={0.6} />
        </mesh>
      </group>
    </group>
  );
}
