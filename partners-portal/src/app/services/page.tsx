import ServiceCatalog from '@/components/enterprise/ServiceCatalog'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function ServicesPage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <Link href="/">
                <h1 className="text-2xl font-bold cursor-pointer">GridWorks</h1>
              </Link>
              <div className="hidden md:flex items-center space-x-6">
                <Link href="/services" className="text-sm font-medium text-primary border-b-2 border-primary">Services</Link>
                <Link href="/pricing" className="text-sm font-medium hover:text-primary">Pricing</Link>
                <Link href="/docs" className="text-sm font-medium hover:text-primary">Documentation</Link>
                <Link href="/support" className="text-sm font-medium hover:text-primary">Support</Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline">Sign In</Button>
              <Button>Get Started</Button>
            </div>
          </nav>
        </div>
      </header>

      {/* Services Content */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">GridWorks B2B Infrastructure Services</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Complete enterprise-grade financial infrastructure services designed for Fortune 500 companies. 
              Deploy in 48 hours, scale to millions.
            </p>
          </div>
          
          <ServiceCatalog />
        </div>
      </section>
    </div>
  )
}