import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, Book, Code, FileText, Zap } from 'lucide-react'
import Link from 'next/link'

export default function DocsPage() {
  const docSections = [
    {
      title: "Quick Start Guide",
      description: "Get up and running with GridWorks in under 5 minutes",
      icon: <Zap className="h-8 w-8" />,
      badge: "Popular",
      items: [
        "Installation & Setup",
        "Authentication",
        "First API Call",
        "Error Handling"
      ]
    },
    {
      title: "SDK Documentation", 
      description: "Complete guides for all our SDKs",
      icon: <Code className="h-8 w-8" />,
      badge: "Updated",
      items: [
        "TypeScript/JavaScript SDK",
        "Python SDK", 
        "REST API Reference",
        "WebSocket SDK"
      ]
    },
    {
      title: "API Reference",
      description: "Detailed API documentation for all services",
      icon: <Book className="h-8 w-8" />,
      badge: null,
      items: [
        "AI Suite APIs",
        "Anonymous Services APIs",
        "Trading APIs",
        "Banking APIs"
      ]
    },
    {
      title: "Enterprise Guides",
      description: "Enterprise deployment and configuration",
      icon: <FileText className="h-8 w-8" />,
      badge: "Enterprise",
      items: [
        "Enterprise Onboarding",
        "Security & Compliance",
        "Scaling & Performance",
        "White-label Solutions"
      ]
    }
  ]

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
                <Link href="/services" className="text-sm font-medium hover:text-primary">Services</Link>
                <Link href="/pricing" className="text-sm font-medium hover:text-primary">Pricing</Link>
                <Link href="/docs" className="text-sm font-medium text-primary border-b-2 border-primary">Documentation</Link>
                <Link href="/support" className="text-sm font-medium hover:text-primary">Support</Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/auth/signin">
                <Button variant="outline">Sign In</Button>
              </Link>
              <Link href="/auth/signup">
                <Button>Get Started</Button>
              </Link>
            </div>
          </nav>
        </div>
      </header>

      {/* Documentation Content */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h1 className="text-5xl font-bold mb-6">Documentation</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Comprehensive guides and API references to help you integrate GridWorks B2B infrastructure services
            </p>
          </div>

          {/* Quick Start Banner */}
          <Card className="mb-12 bg-gradient-to-r from-primary/5 to-blue-50">
            <CardContent className="p-8">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold mb-2">Ready to get started?</h3>
                  <p className="text-muted-foreground mb-4">
                    Follow our quick start guide to make your first API call in under 5 minutes
                  </p>
                  <div className="space-x-4">
                    <Button>
                      Quick Start Guide
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                    <Button variant="outline">
                      View Code Examples
                    </Button>
                  </div>
                </div>
                <div className="hidden lg:block">
                  <Code className="h-32 w-32 text-primary/20" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Documentation Sections */}
          <div className="grid md:grid-cols-2 gap-8 mb-16">
            {docSections.map((section, index) => (
              <Card key={index} className="cursor-pointer transition-all hover:shadow-lg">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-primary/10 rounded-lg">
                        {section.icon}
                      </div>
                      <div>
                        <CardTitle className="text-xl">{section.title}</CardTitle>
                        {section.badge && (
                          <Badge variant="secondary" className="mt-1">
                            {section.badge}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  <CardDescription>{section.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {section.items.map((item, i) => (
                      <li key={i} className="flex items-center space-x-2 text-sm hover:text-primary cursor-pointer">
                        <ArrowRight className="h-3 w-3" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Code Example Preview */}
          <div className="mb-16">
            <h3 className="text-2xl font-bold mb-8 text-center">Code Examples</h3>
            <div className="grid md:grid-cols-2 gap-8">
              <Card>
                <CardHeader>
                  <CardTitle>TypeScript/JavaScript</CardTitle>
                  <CardDescription>Quick integration example</CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-gray-900 text-green-400 p-4 rounded text-sm overflow-x-auto">
{`import { GridWorksSDK } from '@gridworks/b2b-sdk';

const client = new GridWorksSDK({
  apiKey: 'your-api-key',
  environment: 'production'
});

// Get AI support response
const response = await client.aiSuite
  .getSupportResponse('Hello');

console.log(response.reply);`}
                  </pre>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Python</CardTitle>
                  <CardDescription>Python SDK example</CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-gray-900 text-green-400 p-4 rounded text-sm overflow-x-auto">
{`from gridworks_sdk import GridWorksSDK

client = GridWorksSDK(
    api_key="your-api-key",
    environment="production"
)

# Get portfolio data
portfolio = client.trading.get_portfolio()
print(f"Total value: ₹{portfolio.total_value}")`}
                  </pre>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Resources */}
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-8">Additional Resources</h3>
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <Link href="https://github.com/raosunjoy/gridworks-infra" target="_blank">
                <Card className="cursor-pointer hover:shadow-lg transition-all">
                  <CardContent className="p-6 text-center">
                    <Code className="h-12 w-12 mx-auto mb-4 text-primary" />
                    <h4 className="font-semibold mb-2">GitHub Repository</h4>
                    <p className="text-sm text-muted-foreground">View source code and examples</p>
                  </CardContent>
                </Card>
              </Link>

              <Link href="/support">
                <Card className="cursor-pointer hover:shadow-lg transition-all">
                  <CardContent className="p-6 text-center">
                    <FileText className="h-12 w-12 mx-auto mb-4 text-primary" />
                    <h4 className="font-semibold mb-2">Support Center</h4>
                    <p className="text-sm text-muted-foreground">Get help from our team</p>
                  </CardContent>
                </Card>
              </Link>

              <Card className="cursor-pointer hover:shadow-lg transition-all">
                <CardContent className="p-6 text-center">
                  <Book className="h-12 w-12 mx-auto mb-4 text-primary" />
                  <h4 className="font-semibold mb-2">API Status</h4>
                  <p className="text-sm text-muted-foreground">Real-time API health</p>
                  <Badge variant="outline" className="mt-2 bg-green-50 text-green-700">
                    All Systems Operational
                  </Badge>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}