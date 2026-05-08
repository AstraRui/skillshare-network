export const nodes = [
  { id: 'n1', x: 18, y: 18, type: 'user' },
  { id: 'n2', x: 50, y: 12, type: 'user' },
  { id: 'n3', x: 82, y: 40, type: 'user' },
  { id: 'n4', x: 24, y: 74, type: 'user' },
  { id: 'n5', x: 52, y: 84, type: 'trend' },
]

export const links = [
  { from: 'n1', to: 'center' },
  { from: 'n2', to: 'center' },
  { from: 'n3', to: 'center' },
  { from: 'n4', to: 'center' },
  { from: 'n5', to: 'center' },
  { from: 'n1', to: 'n5' },
  { from: 'n4', to: 'n2' },
]

export function getPoint(id) {
  if (id === 'center') {
    return { x: 50, y: 50 }
  }
  return nodes.find((node) => node.id === id)
}
