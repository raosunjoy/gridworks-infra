import ServiceCatalog from '@/components/enterprise/ServiceCatalog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowRight, BarChart3, Lock, Zap, Globe } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <h1 className="text-2xl font-bold">GridWorks</h1>
              <div className="hidden md:flex items-center space-x-6">
                <a href="#services" className="text-sm font-medium hover:text-primary">Services</a>
                <a href="#pricing" className="text-sm font-medium hover:text-primary">Pricing</a>
                <a href="#docs" className="text-sm font-medium hover:text-primary">Documentation</a>
                <a href="#support" className="text-sm font-medium hover:text-primary">Support</a>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline">Sign In</Button>
              <Button>Get Started</Button>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-b from-primary/5 to-background">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-5xl font-bold mb-6">
              The AWS of Financial Services
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Enterprise-grade B2B infrastructure that powers financial innovation. 
              Deploy in 48 hours, scale to millions.
            </p>
            <div className="flex justify-center gap-4">
              <Button size="lg">
                Schedule Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button size="lg" variant="outline">
                View Documentation
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold mb-4">Enterprise-Ready Infrastructure</h3>
            <p className="text-lg text-muted-foreground">
              Built for Fortune 500 companies and scaled for startups
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader>
                <Zap className="h-10 w-10 text-primary mb-4" />
                <CardTitle>48-Hour Deployment</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Complete enterprise integration in 48 hours vs 6-month industry standard
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Lock className="h-10 w-10 text-primary mb-4" />
                <CardTitle>Zero-Knowledge Proofs</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  World's first anonymous portfolio management with quantum-resistant encryption
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Globe className="h-10 w-10 text-primary mb-4" />
                <CardTitle>11 Languages</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  AI-powered support in Hindi, English, Tamil, Telugu, and 7 more languages
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <BarChart3 className="h-10 w-10 text-primary mb-4" />
                <CardTitle>100% Test Coverage</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Enterprise-grade reliability with 1,000+ test cases and comprehensive validation
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Service Catalog Section */}
      <section className="py-20 bg-secondary/20">
        <div className="container mx-auto px-4">
          <ServiceCatalog />
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <Card className="max-w-4xl mx-auto">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl">Ready to Transform Your Financial Services?</CardTitle>
              <CardDescription className="text-lg">
                Join Fortune 500 companies already using GridWorks infrastructure
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <div className="flex justify-center gap-4">
                <Button size="lg">
                  Start Free Trial
                </Button>
                <Button size="lg" variant="outline">
                  Contact Sales
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <p className="text-sm text-muted-foreground">
              © 2025 GridWorks B2B Infrastructure. All rights reserved.
            </p>
            <div className="flex gap-6">
              <a href="#" className="text-sm text-muted-foreground hover:text-primary">Privacy</a>
              <a href="#" className="text-sm text-muted-foreground hover:text-primary">Terms</a>
              <a href="#" className="text-sm text-muted-foreground hover:text-primary">Security</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}