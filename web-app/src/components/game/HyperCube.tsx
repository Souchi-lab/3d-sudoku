"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";
import * as THREE from "three";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type LayerFilter = { axis: "x" | "y" | "z"; index: number } | null;

interface HyperCubeProps {
    board: (number | null)[][][];
    N: number;
    onCellClick?: (pos: [number, number, number]) => void;
    selectedPos?: [number, number, number] | null;
    lastPlacedPos?: [number, number, number] | null;
    isShaking?: boolean;
    /** When set, only cells on this layer are fully visible; others fade out. */
    layerFilter?: LayerFilter;
    /**
     * Set of "i-j-k" keys for cells that belong to a newly completed line/slice.
     * These cells play a white emissive burst animation.
     */
    flashingCells?: Set<string>;
    /** performance.now() timestamp when the flash started (ms). */
    flashStartTime?: number;
    /** Position of the hint cell — blinks cyan to guide the player. */
    hintPos?: [number, number, number] | null;
}

// ---------------------------------------------------------------------------
// SoChi BLOCKS colour palette
// ---------------------------------------------------------------------------
const NUMBER_COLORS: Record<number, string> = {
    1: "#2d7ee8",
    2: "#2ec47a",
    3: "#e84444",
    4: "#f5a623",
    5: "#9b5de5",
};

const EMPTY_CELL_COLOR  = "#e8e8e8";
const SELECTED_COLOR    = "#ff8c00";
const LAST_PLACED_COLOR = "#2e7d32";
const HINT_COLOR        = "#00e5ff";   // cyan hint blink

// ---------------------------------------------------------------------------
// Helper: is a cell on the active layer?
// ---------------------------------------------------------------------------
function isOnLayer(pos: [number, number, number], filter: LayerFilter): boolean {
    if (!filter) return true;
    const { axis, index } = filter;
    if (axis === "x") return pos[0] === index;
    if (axis === "y") return pos[1] === index;
    return pos[2] === index;
}

// ---------------------------------------------------------------------------
// Single cell mesh
// ---------------------------------------------------------------------------
function CellBox({
    pos,
    value,
    isSelected,
    isLastPlaced,
    dimmed,
    isFlashing,
    flashStartTime,
    isHint,
    onClick,
}: {
    pos: [number, number, number];
    value: number | null;
    isSelected: boolean;
    isLastPlaced: boolean;
    dimmed: boolean;
    isFlashing: boolean;
    flashStartTime: number;
    isHint: boolean;
    onClick: () => void;
}) {
    const meshRef = useRef<THREE.Mesh>(null);

    const color = useMemo(() => {
        if (isSelected) return SELECTED_COLOR;
        if (value === null) return EMPTY_CELL_COLOR;
        return NUMBER_COLORS[value] ?? "#999999";
    }, [value, isSelected]);

    const opacity = dimmed
        ? 0.04
        : value === null
            ? 0.18
            : 0.82;

    const emissiveIntensity = dimmed ? 0 : isSelected ? 0.6 : isLastPlaced ? 0.5 : 0.2;
    const emissive = isSelected ? SELECTED_COLOR : isLastPlaced ? LAST_PLACED_COLOR : color;

    // Animate emissive/color for flash and hint effects
    useFrame(() => {
        if (!meshRef.current) return;
        const mat = meshRef.current.material as THREE.MeshStandardMaterial;

        if (isFlashing && flashStartTime > 0) {
            const elapsed = (performance.now() - flashStartTime) / 1000;
            if (elapsed < 1.4) {
                // Decaying sine burst: 2.5 full pulses over 1.4s, fading out
                const t = elapsed / 1.4;
                const burst = Math.sin(t * Math.PI * 5) * Math.pow(1 - t, 0.5);
                mat.emissiveIntensity = Math.max(emissiveIntensity, Math.max(0, burst) * 2.5 + 0.2);
                mat.emissive.set("#ffffff");
                return;
            }
            // Animation done — fall through to restore
        }

        if (isHint) {
            // Blink at ~4 Hz
            const blink = (Math.sin((performance.now() / 250) * Math.PI) + 1) / 2;
            mat.emissiveIntensity = 0.4 + blink * 1.4;
            mat.emissive.set(HINT_COLOR);
            mat.color.set(HINT_COLOR);
            return;
        }

        // Restore base material values
        mat.emissiveIntensity = emissiveIntensity;
        mat.emissive.set(emissive);
        mat.color.set(color);
    });

    return (
        <mesh
            position={[pos[0] - 1, pos[1] - 1, pos[2] - 1]}
            onClick={(e) => { e.stopPropagation(); if (!dimmed) onClick(); }}
            ref={meshRef}
        >
            <boxGeometry args={[0.82, 0.82, 0.82]} />
            <meshStandardMaterial
                color={color}
                transparent
                opacity={opacity}
                emissive={emissive}
                emissiveIntensity={emissiveIntensity}
                roughness={0.6}
                metalness={0.0}
            />

            {/* Number label — hidden when dimmed */}
            {value !== null && !dimmed && (
                <Text
                    position={[0, 0, 0.42]}
                    fontSize={0.38}
                    color="white"
                    anchorX="center"
                    anchorY="middle"
                    fontWeight={700}
                >
                    {value}
                </Text>
            )}

            {/* Edges — only for visible, active cells */}
            {isLastPlaced && !dimmed && (
                <lineSegments>
                    <edgesGeometry args={[new THREE.BoxGeometry(0.87, 0.87, 0.87)]} />
                    <lineBasicMaterial color={LAST_PLACED_COLOR} linewidth={2} />
                </lineSegments>
            )}
            {isSelected && !dimmed && (
                <lineSegments>
                    <edgesGeometry args={[new THREE.BoxGeometry(0.87, 0.87, 0.87)]} />
                    <lineBasicMaterial color={SELECTED_COLOR} linewidth={2} />
                </lineSegments>
            )}
            {isHint && !dimmed && (
                <lineSegments>
                    <edgesGeometry args={[new THREE.BoxGeometry(0.92, 0.92, 0.92)]} />
                    <lineBasicMaterial color={HINT_COLOR} linewidth={2} />
                </lineSegments>
            )}
        </mesh>
    );
}

// ---------------------------------------------------------------------------
// Scene (shake animation wrapper)
// ---------------------------------------------------------------------------
function Scene({
    cells,
    isShaking,
    onCellClick,
    flashStartTime,
}: {
    cells: {
        pos: [number, number, number];
        value: number | null;
        isSelected: boolean;
        isLastPlaced: boolean;
        dimmed: boolean;
        isFlashing: boolean;
        isHint: boolean;
    }[];
    isShaking?: boolean;
    onCellClick: (pos: [number, number, number]) => void;
    flashStartTime: number;
}) {
    const groupRef = useRef<THREE.Group>(null);

    useFrame(() => {
        if (!groupRef.current) return;
        if (isShaking) {
            groupRef.current.position.x = (Math.random() - 0.5) * 0.1;
            groupRef.current.position.y = (Math.random() - 0.5) * 0.1;
        } else {
            groupRef.current.position.set(0, 0, 0);
        }
    });

    return (
        <group ref={groupRef}>
            {cells.map((cell) => (
                <CellBox
                    key={cell.pos.join("-")}
                    pos={cell.pos}
                    value={cell.value}
                    isSelected={cell.isSelected}
                    isLastPlaced={cell.isLastPlaced}
                    dimmed={cell.dimmed}
                    isFlashing={cell.isFlashing}
                    flashStartTime={flashStartTime}
                    isHint={cell.isHint}
                    onClick={() => onCellClick(cell.pos)}
                />
            ))}
        </group>
    );
}

// ---------------------------------------------------------------------------
// HyperCube widget
// ---------------------------------------------------------------------------
export default function HyperCube({
    board, N, onCellClick, selectedPos, lastPlacedPos, isShaking, layerFilter,
    flashingCells, flashStartTime = 0, hintPos,
}: HyperCubeProps) {
    const cells = useMemo(() => {
        const list = [];
        for (let i = 0; i < N; i++) {
            for (let j = 0; j < N; j++) {
                for (let k = 0; k < N; k++) {
                    const pos = [i, j, k] as [number, number, number];
                    const key = `${i}-${j}-${k}`;
                    list.push({
                        pos,
                        value: board[i][j][k],
                        isSelected:
                            selectedPos?.[0] === i &&
                            selectedPos?.[1] === j &&
                            selectedPos?.[2] === k,
                        isLastPlaced:
                            lastPlacedPos?.[0] === i &&
                            lastPlacedPos?.[1] === j &&
                            lastPlacedPos?.[2] === k,
                        dimmed: layerFilter !== undefined && layerFilter !== null
                            ? !isOnLayer(pos, layerFilter)
                            : false,
                        isFlashing: flashingCells ? flashingCells.has(key) : false,
                        isHint:
                            hintPos !== null && hintPos !== undefined &&
                            hintPos[0] === i && hintPos[1] === j && hintPos[2] === k,
                    });
                }
            }
        }
        return list;
    }, [board, N, selectedPos, lastPlacedPos, layerFilter, flashingCells, hintPos]);

    return (
        <div
            style={{ touchAction: "none" }}
            className={`w-full h-[min(560px,50svh)] bg-white rounded-xl overflow-hidden border transition-all duration-75 shadow-sm ${
                isShaking
                    ? "border-[#e53e3e] shadow-[0_0_0_3px_rgba(229,62,62,0.15)]"
                    : "border-[#dddddd]"
            }`}
        >
            <Canvas camera={{ position: [5, 5, 5], fov: 45 }}>
                <ambientLight intensity={1.4} />
                <directionalLight position={[6, 8, 6]} intensity={0.6} />
                <Scene
                    cells={cells}
                    isShaking={isShaking}
                    onCellClick={onCellClick ?? (() => {})}
                    flashStartTime={flashStartTime}
                />
                <OrbitControls makeDefault />
            </Canvas>
        </div>
    );
}
