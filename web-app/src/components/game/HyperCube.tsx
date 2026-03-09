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
    /** Position of the most recently placed cell — plays a scale-pop animation. */
    justPlacedPos?: [number, number, number] | null;
    /** performance.now() timestamp when the last cell was placed (ms). */
    justPlacedTime?: number;
    /** Set of "i-j-k" keys for pre-filled initial hint cells (visually distinct). */
    hintCellKeys?: Set<string>;
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
const INITIAL_HINT_COLOR = "#f5a623"; // gold border for pre-filled cells

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
    isJustPlaced,
    justPlacedTime,
    isHighlighted,
    isInitialHint,
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
    isJustPlaced: boolean;
    justPlacedTime: number;
    isHighlighted: boolean;
    isInitialHint: boolean;
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

    // Animate scale, emissive/color for flash, hint, scale-pop, and highlight
    useFrame(() => {
        if (!meshRef.current) return;
        const mat = meshRef.current.material as THREE.MeshStandardMaterial;

        // 1. Scale-pop (H1): just-placed cell bounces 1.0 → 1.25 → 1.0 over 350ms
        if (isJustPlaced && justPlacedTime > 0) {
            const t = Math.min(1, (performance.now() - justPlacedTime) / 350);
            if (t < 1) {
                const s = t < 0.55
                    ? 1 + (t / 0.55) * 0.25
                    : 1.25 - ((t - 0.55) / 0.45) * 0.25;
                meshRef.current.scale.set(s, s, s);
            } else {
                meshRef.current.scale.set(1, 1, 1);
            }
        } else {
            meshRef.current.scale.set(1, 1, 1);
        }

        // 2. Flash burst animation
        if (isFlashing && flashStartTime > 0) {
            const elapsed = (performance.now() - flashStartTime) / 1000;
            if (elapsed < 1.4) {
                const t = elapsed / 1.4;
                const burst = Math.sin(t * Math.PI * 5) * Math.pow(1 - t, 0.5);
                mat.emissiveIntensity = Math.max(emissiveIntensity, Math.max(0, burst) * 2.5 + 0.2);
                mat.emissive.set("#ffffff");
                mat.opacity = opacity;
                return;
            }
        }

        // 3. Hint blink (cyan)
        if (isHint) {
            const blink = (Math.sin((performance.now() / 250) * Math.PI) + 1) / 2;
            mat.emissiveIntensity = 0.4 + blink * 1.4;
            mat.emissive.set(HINT_COLOR);
            mat.color.set(HINT_COLOR);
            mat.opacity = opacity;
            return;
        }

        // 4. Restore base material + line-highlight boost (M5)
        mat.color.set(color);
        if (isHighlighted && !isSelected && !dimmed) {
            mat.emissive.set(value === null ? "#cccccc" : color);
            mat.emissiveIntensity = emissiveIntensity + 0.2;
            mat.opacity = value === null ? 0.30 : Math.min(0.95, opacity + 0.10);
        } else {
            mat.emissive.set(emissive);
            mat.emissiveIntensity = emissiveIntensity;
            mat.opacity = opacity;
        }
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
                metalness={isInitialHint ? 0.15 : 0.0}
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

            {/* Edges */}
            {isInitialHint && !dimmed && !isSelected && !isLastPlaced && (
                <lineSegments>
                    <edgesGeometry args={[new THREE.BoxGeometry(0.84, 0.84, 0.84)]} />
                    <lineBasicMaterial color={INITIAL_HINT_COLOR} linewidth={1} />
                </lineSegments>
            )}
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
    justPlacedTime,
}: {
    cells: {
        pos: [number, number, number];
        value: number | null;
        isSelected: boolean;
        isLastPlaced: boolean;
        dimmed: boolean;
        isFlashing: boolean;
        isHint: boolean;
        isJustPlaced: boolean;
        isHighlighted: boolean;
        isInitialHint: boolean;
    }[];
    isShaking?: boolean;
    onCellClick: (pos: [number, number, number]) => void;
    flashStartTime: number;
    justPlacedTime: number;
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
                    isJustPlaced={cell.isJustPlaced}
                    justPlacedTime={justPlacedTime}
                    isHighlighted={cell.isHighlighted}
                    isInitialHint={cell.isInitialHint}
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
    justPlacedPos, justPlacedTime = 0, hintCellKeys,
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
                        isJustPlaced:
                            justPlacedPos !== null && justPlacedPos !== undefined &&
                            justPlacedPos[0] === i && justPlacedPos[1] === j && justPlacedPos[2] === k,
                        // M5: highlight cells sharing any axis with the selected cell
                        isHighlighted:
                            selectedPos !== null && selectedPos !== undefined &&
                            !(selectedPos[0] === i && selectedPos[1] === j && selectedPos[2] === k) &&
                            (selectedPos[0] === i || selectedPos[1] === j || selectedPos[2] === k),
                        // H4: pre-filled initial hint cells
                        isInitialHint: hintCellKeys ? hintCellKeys.has(key) : false,
                    });
                }
            }
        }
        return list;
    }, [board, N, selectedPos, lastPlacedPos, layerFilter, flashingCells, hintPos, justPlacedPos, hintCellKeys]);

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
                    justPlacedTime={justPlacedTime}
                />
                <OrbitControls makeDefault enableDamping dampingFactor={0.1} />
            </Canvas>
        </div>
    );
}
