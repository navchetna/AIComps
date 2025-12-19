import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'

export const dynamic = 'force-dynamic'
export const runtime = 'nodejs'

export default function ViewLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
