import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GraphNode, GraphEdge } from "../types";
import { RotateCw, ZoomIn, ZoomOut, Maximize2, RefreshCw } from "lucide-react";

interface Globe3DProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onSelectNode: (nodeId: number) => void;
  selectedNodeId?: number | null;
  highlightedPathNodeIds?: string[];
}

export const Globe3D: React.FC<Globe3DProps> = ({
  nodes,
  edges,
  onSelectNode,
  selectedNodeId,
  highlightedPathNodeIds = [],
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [autoRotate, setAutoRotate] = useState(true);

  // Three.js instances ref
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const globeGroupRef = useRef<THREE.Group | null>(null);
  const nodeMeshesRef = useRef<Map<string, THREE.Mesh>>(new Map());

  // Mouse interaction state
  const isDraggingRef = useRef(false);
  const previousMousePositionRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    // 1. Scene setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    // 2. Camera setup
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 2000);
    camera.position.z = 320;
    cameraRef.current = camera;

    // 3. Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 4. Globe Master Group
    const globeGroup = new THREE.Group();
    scene.add(globeGroup);
    globeGroupRef.current = globeGroup;

    // 5. Wireframe Earth Sphere
    const globeRadius = 100;
    const sphereGeometry = new THREE.SphereGeometry(globeRadius, 36, 36);
    const sphereMaterial = new THREE.MeshBasicMaterial({
      color: 0x071526,
      transparent: true,
      opacity: 0.85,
    });
    const globeMesh = new THREE.Mesh(sphereGeometry, sphereMaterial);
    globeGroup.add(globeMesh);

    // Wireframe grid lines on globe
    const wireframeMaterial = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      wireframe: true,
      transparent: true,
      opacity: 0.12,
    });
    const wireframeMesh = new THREE.Mesh(sphereGeometry, wireframeMaterial);
    globeGroup.add(wireframeMesh);

    // Glowing outer atmosphere halo
    const atmosphereGeometry = new THREE.SphereGeometry(globeRadius * 1.08, 32, 32);
    const atmosphereMaterial = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.05,
      side: THREE.BackSide,
    });
    const atmosphereMesh = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    globeGroup.add(atmosphereMesh);

    // Equator and Latitude Guide Rings
    const ringGeo = new THREE.RingGeometry(globeRadius * 1.01, globeRadius * 1.02, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.25,
    });
    const equatorRing = new THREE.Mesh(ringGeo, ringMat);
    equatorRing.rotation.x = Math.PI / 2;
    globeGroup.add(equatorRing);

    // 6. Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x00f0ff, 2, 800);
    pointLight.position.set(200, 200, 300);
    scene.add(pointLight);

    // 7. Raycaster for hover/click detection
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onPointerMove = (e: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(Array.from(nodeMeshesRef.current.values()));

      if (intersects.length > 0) {
        const mesh = intersects[0].object as THREE.Mesh;
        const nodeData = mesh.userData as GraphNode;
        setHoveredNode(nodeData);
        containerRef.current!.style.cursor = "pointer";
      } else {
        setHoveredNode(null);
        if (!isDraggingRef.current && containerRef.current) {
          containerRef.current.style.cursor = "default";
        }
      }
    };

    const onClick = (e: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(Array.from(nodeMeshesRef.current.values()));

      if (intersects.length > 0) {
        const mesh = intersects[0].object as THREE.Mesh;
        const nodeData = mesh.userData as GraphNode;
        onSelectNode(nodeData.numeric_id);
      }
    };

    const domElement = renderer.domElement;
    domElement.addEventListener("mousemove", onPointerMove);
    domElement.addEventListener("click", onClick);

    // Mouse drag to rotate controls
    const onMouseDown = (e: MouseEvent) => {
      isDraggingRef.current = true;
      previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
    };

    const onMouseDrag = (e: MouseEvent) => {
      if (!isDraggingRef.current || !globeGroupRef.current) return;
      const deltaX = e.clientX - previousMousePositionRef.current.x;
      const deltaY = e.clientY - previousMousePositionRef.current.y;

      globeGroupRef.current.rotation.y += deltaX * 0.005;
      globeGroupRef.current.rotation.x += deltaY * 0.005;

      previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
    };

    const onMouseUp = () => {
      isDraggingRef.current = false;
    };

    domElement.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseDrag);
    window.addEventListener("mouseup", onMouseUp);

    // Zoom on wheel
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      if (!cameraRef.current) return;
      cameraRef.current.position.z = Math.max(180, Math.min(600, cameraRef.current.position.z + e.deltaY * 0.25));
    };
    domElement.addEventListener("wheel", onWheel, { passive: false });

    // 8. Animation loop
    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      if (globeGroupRef.current && autoRotate && !isDraggingRef.current) {
        globeGroupRef.current.rotation.y += 0.002;
      }

      renderer.render(scene, camera);
    };
    animate();

    // Resize handler
    const handleResize = () => {
      if (!containerRef.current || !rendererRef.current || !cameraRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      cameraRef.current.aspect = w / h;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      domElement.removeEventListener("mousemove", onPointerMove);
      domElement.removeEventListener("click", onClick);
      domElement.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mousemove", onMouseDrag);
      window.removeEventListener("mouseup", onMouseUp);
      domElement.removeEventListener("wheel", onWheel);
      window.removeEventListener("resize", handleResize);

      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [autoRotate, onSelectNode]);

  // Update nodes and edges when data or highlights change
  useEffect(() => {
    if (!globeGroupRef.current) return;
    const globeGroup = globeGroupRef.current;

    // Clear previous node and edge meshes
    nodeMeshesRef.current.forEach((mesh) => globeGroup.remove(mesh));
    nodeMeshesRef.current.clear();

    const edgesToRemove: THREE.Object3D[] = [];
    globeGroup.children.forEach((child) => {
      if (child.name === "graph-edge" || child.name === "node-glow") {
        edgesToRemove.push(child);
      }
    });
    edgesToRemove.forEach((c) => globeGroup.remove(c));

    const nodePositions = new Map<string, THREE.Vector3>();

    // 1. Create 3D Nodes
    nodes.forEach((node) => {
      let pos: THREE.Vector3;
      const globeRadius = 100;

      // If geocoded, map lat/lng to sphere
      if (node.has_geocoding && node.lat !== null && node.lng !== null && node.lat !== undefined && node.lng !== undefined) {
        const phi = (90 - node.lat) * (Math.PI / 180);
        const theta = (node.lng + 180) * (Math.PI / 180);
        const r = globeRadius * 1.03;
        pos = new THREE.Vector3(
          -(r * Math.sin(phi) * Math.cos(theta)),
          r * Math.cos(phi),
          r * Math.sin(phi) * Math.sin(theta)
        );
      } else {
        // Use spherical Fibonacci position calculated by backend
        pos = new THREE.Vector3(node.x || 0, node.y || 0, node.z || 0).normalize().multiplyScalar(globeRadius * 1.04);
      }

      nodePositions.set(node.id, pos);

      const isSelected = selectedNodeId === node.numeric_id;
      const isPathHighlight = highlightedPathNodeIds.includes(node.id);

      const nodeSize = isSelected || isPathHighlight ? 4.5 : node.risk_score >= 80 ? 3.5 : 2.5;
      const nodeGeo = new THREE.SphereGeometry(nodeSize, 16, 16);
      const nodeColor = isPathHighlight ? 0xffff00 : new THREE.Color(node.color);

      const nodeMat = new THREE.MeshBasicMaterial({
        color: nodeColor,
      });

      const mesh = new THREE.Mesh(nodeGeo, nodeMat);
      mesh.position.copy(pos);
      mesh.userData = node;
      globeGroup.add(mesh);
      nodeMeshesRef.current.set(node.id, mesh);

      // Glowing halo for selected or high risk nodes
      if (isSelected || isPathHighlight || node.risk_score >= 80) {
        const haloGeo = new THREE.RingGeometry(nodeSize * 1.3, nodeSize * 2.0, 16);
        const haloMat = new THREE.MeshBasicMaterial({
          color: nodeColor,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.6,
        });
        const haloMesh = new THREE.Mesh(haloGeo, haloMat);
        haloMesh.position.copy(pos);
        haloMesh.lookAt(new THREE.Vector3(0, 0, 0));
        haloMesh.name = "node-glow";
        globeGroup.add(haloMesh);
      }
    });

    // 2. Create Curved Relationship Arcs connecting correlated nodes
    edges.forEach((edge) => {
      const srcPos = nodePositions.get(edge.source);
      const tgtPos = nodePositions.get(edge.target);

      if (!srcPos || !tgtPos) return;

      // Create quadratic bezier curve elevating above the globe surface
      const midPoint = new THREE.Vector3().addVectors(srcPos, tgtPos).multiplyScalar(0.5);
      const distance = srcPos.distanceTo(tgtPos);
      const elevation = Math.min(50, Math.max(15, distance * 0.25));
      midPoint.normalize().multiplyScalar(100 + elevation);

      const curve = new THREE.QuadraticBezierCurve3(srcPos, midPoint, tgtPos);
      const points = curve.getPoints(24);
      const geometry = new THREE.BufferGeometry().setFromPoints(points);

      const isPathEdge =
        highlightedPathNodeIds.includes(edge.source) &&
        highlightedPathNodeIds.includes(edge.target);

      const edgeColor = isPathEdge ? 0xffff00 : new THREE.Color(edge.color);
      const material = new THREE.LineBasicMaterial({
        color: edgeColor,
        transparent: true,
        opacity: isPathEdge ? 0.95 : edge.confidence >= 0.9 ? 0.75 : 0.45,
        linewidth: isPathEdge ? 2 : 1,
      });

      const line = new THREE.Line(geometry, material);
      line.name = "graph-edge";
      globeGroup.add(line);
    });
  }, [nodes, edges, selectedNodeId, highlightedPathNodeIds]);

  // Controls actions
  const zoomIn = () => {
    if (!cameraRef.current) return;
    cameraRef.current.position.z = Math.max(180, cameraRef.current.position.z - 40);
  };

  const zoomOut = () => {
    if (!cameraRef.current) return;
    cameraRef.current.position.z = Math.min(550, cameraRef.current.position.z + 40);
  };

  const resetView = () => {
    if (!cameraRef.current || !globeGroupRef.current) return;
    cameraRef.current.position.set(0, 0, 320);
    globeGroupRef.current.rotation.set(0, 0, 0);
  };

  return (
    <div className="relative w-full h-full overflow-hidden select-none bg-slate-950/60 rounded-xl border border-cyan-500/20">
      {/* 3D Canvas Container */}
      <div ref={containerRef} className="w-full h-full" />

      {/* Cyber Compass / Coordinates HUD in top-left */}
      <div className="absolute top-4 left-4 p-3 rounded-lg bg-slate-950/80 border border-cyan-500/30 backdrop-blur-md text-[11px] font-mono text-cyan-300 pointer-events-none">
        <div className="flex items-center space-x-2 text-cyan-400 font-bold mb-1">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>TACTICAL 3D SCAM NETWORK GLOBE</span>
        </div>
        <div className="text-slate-400">
          Entities: <span className="text-slate-200">{nodes.length}</span> | Linked Edges:{" "}
          <span className="text-slate-200">{edges.length}</span>
        </div>
        <div className="text-slate-400">
          Render: <span className="text-emerald-400">Three.js WebGL (60 FPS)</span>
        </div>
      </div>

      {/* Interactive Floating Hover Card */}
      {hoveredNode && (
        <div className="absolute bottom-6 left-6 p-4 rounded-xl bg-slate-900/90 border border-cyan-400/50 backdrop-blur-xl shadow-2xl text-xs font-mono max-w-sm pointer-events-none animate-in fade-in duration-150">
          <div className="flex items-center justify-between gap-3 mb-1.5">
            <span
              className="text-[10px] px-2 py-0.5 rounded font-bold uppercase"
              style={{
                backgroundColor: `${hoveredNode.color}20`,
                color: hoveredNode.color,
                border: `1px solid ${hoveredNode.color}40`,
              }}
            >
              {hoveredNode.type}
            </span>
            <span
              className={`font-bold ${
                hoveredNode.risk_score >= 70 ? "text-rose-400" : "text-amber-400"
              }`}
            >
              Risk: {hoveredNode.risk_score}/100
            </span>
          </div>

          <div className="text-sm font-bold text-slate-100 truncate mb-1">
            {hoveredNode.label}
          </div>

          <div className="text-[11px] text-slate-400 truncate mb-2">
            Value: {hoveredNode.value}
          </div>

          {hoveredNode.has_geocoding && (
            <div className="text-[10px] text-cyan-300">
              Locale: {hoveredNode.lat?.toFixed(2)}°, {hoveredNode.lng?.toFixed(2)}°
            </div>
          )}

          <div className="mt-2 text-[10px] text-cyan-400/80 border-t border-slate-800 pt-1.5">
            Click node to open complete investigation dossier &rarr;
          </div>
        </div>
      )}

      {/* Floating Tactical Control Toolbar in top-right */}
      <div className="absolute top-4 right-4 flex items-center space-x-2">
        <button
          onClick={() => setAutoRotate(!autoRotate)}
          className={`p-2 rounded-lg border text-xs font-mono transition cursor-pointer flex items-center space-x-1.5 ${
            autoRotate
              ? "bg-cyan-950/80 border-cyan-500/50 text-cyan-300"
              : "bg-slate-900/80 border-slate-700 text-slate-400 hover:text-slate-200"
          }`}
          title="Toggle Auto Rotation"
        >
          <RotateCw className={`w-3.5 h-3.5 ${autoRotate ? "animate-spin" : ""}`} />
          <span className="hidden sm:inline">Rotate</span>
        </button>

        <button
          onClick={zoomIn}
          className="p-2 rounded-lg bg-slate-900/80 border border-slate-700 text-slate-300 hover:text-cyan-400 hover:border-cyan-500/40 transition cursor-pointer"
          title="Zoom In"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>

        <button
          onClick={zoomOut}
          className="p-2 rounded-lg bg-slate-900/80 border border-slate-700 text-slate-300 hover:text-cyan-400 hover:border-cyan-500/40 transition cursor-pointer"
          title="Zoom Out"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>

        <button
          onClick={resetView}
          className="p-2 rounded-lg bg-slate-900/80 border border-slate-700 text-slate-300 hover:text-cyan-400 hover:border-cyan-500/40 transition cursor-pointer"
          title="Reset Globe Orientation"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
