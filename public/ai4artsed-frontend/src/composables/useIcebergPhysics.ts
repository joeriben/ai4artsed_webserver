/**
 * Iceberg Physics Composable
 *
 * Provides polygon manipulation functions for the melting iceberg animation.
 * Own implementation - no external library dependencies (license-free).
 */

export interface Point {
  x: number
  y: number
}

/**
 * Calculate the centroid (center of mass) of a polygon
 * Uses the geometric centroid formula for irregular polygons
 */
export function calculateCentroid(polygon: Point[]): Point {
  if (polygon.length === 0) {
    return { x: 0, y: 0 }
  }

  const first = polygon[0]
  if (!first || polygon.length === 1) {
    return { x: first?.x ?? 0, y: first?.y ?? 0 }
  }

  let cx = 0
  let cy = 0
  let area = 0

  for (let i = 0; i < polygon.length; i++) {
    const j = (i + 1) % polygon.length
    const pi = polygon[i]
    const pj = polygon[j]
    if (!pi || !pj) continue

    const cross = pi.x * pj.y - pj.x * pi.y
    area += cross
    cx += (pi.x + pj.x) * cross
    cy += (pi.y + pj.y) * cross
  }

  area /= 2

  if (Math.abs(area) < 0.0001) {
    // Degenerate polygon - return average of points
    const avgX = polygon.reduce((sum, p) => sum + p.x, 0) / polygon.length
    const avgY = polygon.reduce((sum, p) => sum + p.y, 0) / polygon.length
    return { x: avgX, y: avgY }
  }

  cx /= 6 * area
  cy /= 6 * area

  return { x: cx, y: cy }
}

/**
 * Calculate the area of a polygon using the Shoelace formula
 */
export function calculateArea(polygon: Point[]): number {
  if (polygon.length < 3) return 0

  let area = 0
  for (let i = 0; i < polygon.length; i++) {
    const j = (i + 1) % polygon.length
    const pi = polygon[i]
    const pj = polygon[j]
    if (!pi || !pj) continue

    area += pi.x * pj.y
    area -= pj.x * pi.y
  }

  return Math.abs(area / 2)
}

/**
 * Check if a polygon is valid (at least 3 points, non-zero area)
 */
export function isPolygonValid(polygon: Point[]): boolean {
  if (polygon.length < 3) return false
  return calculateArea(polygon) > 10 // Minimum 10 square pixels
}

/**
 * Melt the iceberg by shrinking towards centroid
 *
 * @param polygon - Current polygon points
 * @param temperature - GPU temperature in Celsius (0-100)
 * @param waterLine - Y coordinate of water line
 * @param dt - Delta time in milliseconds
 * @returns New polygon with melted coordinates
 */
export function meltIceberg(
  polygon: Point[],
  temperature: number,
  waterLine: number,
  dt: number
): Point[] {
  if (polygon.length < 3) return polygon

  // Normalize temperature effect (higher temp = faster melting)
  // At 80°C, melt rate is ~0.08% per frame
  const baseMeltRate = (temperature / 1000) * (dt / 16.67) // Normalized to 60fps

  const centroid = calculateCentroid(polygon)

  return polygon.map(point => {
    // Points above water melt faster (exposed to air/sun)
    const isAboveWater = point.y < waterLine
    const meltMultiplier = isAboveWater ? 1.5 : 1.0

    const effectiveMeltRate = baseMeltRate * meltMultiplier * 0.001

    // Shrink towards centroid
    const dx = point.x - centroid.x
    const dy = point.y - centroid.y

    return {
      x: centroid.x + dx * (1 - effectiveMeltRate),
      y: centroid.y + dy * (1 - effectiveMeltRate)
    }
  })
}

/**
 * Simplify a polygon using Douglas-Peucker algorithm
 * Reduces the number of points while preserving shape
 *
 * @param polygon - Input polygon points
 * @param epsilon - Maximum distance threshold (higher = more simplification)
 * @returns Simplified polygon
 */
export function simplifyPolygon(polygon: Point[], epsilon: number = 2): Point[] {
  if (polygon.length <= 2) return polygon

  // Find the point with maximum distance from the line between first and last
  let maxDistance = 0
  let maxIndex = 0

  const start = polygon[0]
  const end = polygon[polygon.length - 1]

  if (!start || !end) return polygon

  for (let i = 1; i < polygon.length - 1; i++) {
    const point = polygon[i]
    if (!point) continue

    const distance = perpendicularDistance(point, start, end)
    if (distance > maxDistance) {
      maxDistance = distance
      maxIndex = i
    }
  }

  // If max distance is greater than epsilon, recursively simplify
  if (maxDistance > epsilon) {
    const left = simplifyPolygon(polygon.slice(0, maxIndex + 1), epsilon)
    const right = simplifyPolygon(polygon.slice(maxIndex), epsilon)

    // Combine results, avoiding duplicate point at maxIndex
    return [...left.slice(0, -1), ...right]
  }

  // Otherwise, return just the endpoints
  return [start, end]
}

/**
 * Calculate perpendicular distance from a point to a line segment
 */
function perpendicularDistance(point: Point, lineStart: Point, lineEnd: Point): number {
  const dx = lineEnd.x - lineStart.x
  const dy = lineEnd.y - lineStart.y

  if (dx === 0 && dy === 0) {
    // Line is a point
    return Math.sqrt(
      (point.x - lineStart.x) ** 2 + (point.y - lineStart.y) ** 2
    )
  }

  const lineLengthSquared = dx * dx + dy * dy

  // Calculate perpendicular distance using cross product method
  const cross = Math.abs(
    (point.y - lineStart.y) * dx - (point.x - lineStart.x) * dy
  )

  return cross / Math.sqrt(lineLengthSquared)
}

/**
 * Calculate the bounding box of a polygon
 */
export function getBoundingBox(polygon: Point[]): {
  minX: number
  minY: number
  maxX: number
  maxY: number
  width: number
  height: number
} {
  if (polygon.length === 0) {
    return { minX: 0, minY: 0, maxX: 0, maxY: 0, width: 0, height: 0 }
  }

  const first = polygon[0]
  if (!first) {
    return { minX: 0, minY: 0, maxX: 0, maxY: 0, width: 0, height: 0 }
  }

  let minX = first.x
  let minY = first.y
  let maxX = first.x
  let maxY = first.y

  for (const point of polygon) {
    minX = Math.min(minX, point.x)
    minY = Math.min(minY, point.y)
    maxX = Math.max(maxX, point.x)
    maxY = Math.max(maxY, point.y)
  }

  return {
    minX,
    minY,
    maxX,
    maxY,
    width: maxX - minX,
    height: maxY - minY
  }
}

/**
 * Scale a polygon to fit within given dimensions while maintaining aspect ratio
 */
export function scalePolygonToFit(
  polygon: Point[],
  targetWidth: number,
  targetHeight: number,
  padding: number = 20
): Point[] {
  const bbox = getBoundingBox(polygon)
  if (bbox.width === 0 || bbox.height === 0) return polygon

  const availableWidth = targetWidth - padding * 2
  const availableHeight = targetHeight - padding * 2

  const scaleX = availableWidth / bbox.width
  const scaleY = availableHeight / bbox.height
  const scale = Math.min(scaleX, scaleY)

  // Center the scaled polygon
  const centerX = targetWidth / 2
  const centerY = targetHeight / 2
  const bboxCenterX = (bbox.minX + bbox.maxX) / 2
  const bboxCenterY = (bbox.minY + bbox.maxY) / 2

  return polygon.map(point => ({
    x: centerX + (point.x - bboxCenterX) * scale,
    y: centerY + (point.y - bboxCenterY) * scale
  }))
}

/**
 * Check if the iceberg has melted away (area below threshold)
 */
export function isMelted(polygon: Point[], threshold: number = 100): boolean {
  return calculateArea(polygon) < threshold
}
