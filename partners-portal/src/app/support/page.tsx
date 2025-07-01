import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Mail, Phone, MessageCircle, Clock, Users, Headphones } from 'lucide-react'
import Link from 'next/link'

export default function SupportPage() {
  const supportTiers = [
    {
      name: "Community Support",
      description: "Self-service resources and community forums",
      icon: <Users className="h-8 w-8" />,
      features: [
        "Documentation & Guides",
        "Community Forums",
        "Knowledge Base",
        "Email Support (48h response)"
      ],
      availability: "24/7 Self-Service",
      price: "Free"
    },
    {
      name: "Professional Support", 
      description: "Direct support for professional plans",
      icon: <Headphones className="h-8 w-8" />,
      features: [
        "Email Support (4h response)",
        "Live Chat Support",
        "Technical Documentation",
        "Integration Assistance"
      ],
      availability: "Business Hours (24/5)",
      price: "Included in Professional Plan"
    },
    {
      name: "Enterprise Support",
      description: "Priority support with dedicated resources",
      icon: <Phone className="h-8 w-8" />,
      features: [
        "Priority Email (1h response)",
        "Phone Support",
        "Dedicated Account Manager",
        "Custom Integration Support",
        "SLA Guarantees"
      ],
      availability: "24/7 Priority Support",
      price: "Included in Enterprise Plan"
    }
  ]

  const contactMethods = [
    {
      title: "Email Support",
      description: "Get help via email for any questions",
      icon: <Mail className="h-6 w-6" />,
      contact: "support@gridworks.com",
      responseTime: "Within 4 hours"
    },
    {
      title: "Live Chat",
      description: "Chat with our support team in real-time",
      icon: <MessageCircle className="h-6 w-6" />,
      contact: "Available in portal",
      responseTime: "Immediate"
    },
    {
      title: "Phone Support",
      description: "Speak directly with our technical team",
      icon: <Phone className="h-6 w-6" />,
      contact: "+91-XXXX-XXXXX",
      responseTime: "Enterprise only"
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
                <Link href="/docs" className="text-sm font-medium hover:text-primary">Documentation</Link>
                <Link href="/support" className="text-sm font-medium text-primary border-b-2 border-primary">Support</Link>
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

      {/* Support Content */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h1 className="text-5xl font-bold mb-6">Support Center</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Get the help you need to succeed with GridWorks. Our support team is here to assist you every step of the way.
            </p>
          </div>

          {/* Status Banner */}
          <Card className="mb-12 bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="font-semibold">All Systems Operational</span>
                </div>
                <Badge variant="outline" className="bg-green-100 text-green-800 border-green-300">
                  99.99% Uptime
                </Badge>
                <span className="text-sm text-muted-foreground">Last updated: 2 minutes ago</span>
              </div>
            </CardContent>
          </Card>

          {/* Contact Methods */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-center mb-8">Get in Touch</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {contactMethods.map((method, index) => (
                <Card key={index} className="cursor-pointer hover:shadow-lg transition-all">
                  <CardHeader className="text-center">
                    <div className="mx-auto p-3 bg-primary/10 rounded-full w-fit mb-4">
                      {method.icon}
                    </div>
                    <CardTitle className="text-lg">{method.title}</CardTitle>
                    <CardDescription>{method.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="text-center">
                    <p className="font-semibold mb-2">{method.contact}</p>
                    <p className="text-sm text-muted-foreground flex items-center justify-center">
                      <Clock className="h-4 w-4 mr-1" />
                      {method.responseTime}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Support Tiers */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-center mb-8">Support Plans</h2>
            <div className="grid md:grid-cols-3 gap-8">
              {supportTiers.map((tier, index) => (
                <Card key={index} className={index === 1 ? 'ring-2 ring-primary' : ''}>
                  <CardHeader className="text-center">
                    <div className="mx-auto p-3 bg-primary/10 rounded-full w-fit mb-4">
                      {tier.icon}
                    </div>
                    <CardTitle className="text-xl">{tier.name}</CardTitle>
                    <CardDescription>{tier.description}</CardDescription>
                    <div className="text-lg font-semibold text-primary">{tier.price}</div>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3 mb-6">
                      {tier.features.map((feature, i) => (
                        <li key={i} className="flex items-center space-x-2 text-sm">
                          <div className="h-2 w-2 bg-primary rounded-full"></div>
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <div className="border-t pt-4">
                      <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        <span>{tier.availability}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* FAQ Section */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-center mb-8">Frequently Asked Questions</h2>
            <div className="max-w-4xl mx-auto space-y-4">
              {[
                {
                  question: "How quickly can I integrate GridWorks services?",
                  answer: "Most integrations can be completed in 48 hours using our comprehensive SDKs and documentation."
                },
                {
                  question: "What programming languages do you support?",
                  answer: "We provide SDKs for TypeScript/JavaScript, Python, and a complete REST API that works with any language."
                },
                {
                  question: "Do you offer custom enterprise solutions?",
                  answer: "Yes, we provide custom solutions, white-label options, and dedicated support for enterprise clients."
                },
                {
                  question: "What are your uptime guarantees?",
                  answer: "We offer 99.5% for Professional, 99.99% for Enterprise, and 99.999% for UHNW tiers."
                }
              ].map((faq, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="text-lg">{faq.question}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{faq.answer}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Emergency Support */}
          <Card className="max-w-4xl mx-auto bg-red-50 border-red-200">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl text-red-700">Emergency Support</CardTitle>
              <CardDescription className="text-red-600">
                For critical production issues affecting your business operations
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <p className="mb-4 text-red-700">
                Enterprise customers: Call our emergency hotline for immediate assistance
              </p>
              <Button variant="destructive">
                <Phone className="h-4 w-4 mr-2" />
                Emergency Hotline: +91-XXXX-EMERGENCY
              </Button>
              <p className="text-sm text-red-600 mt-2">
                Available 24/7 for Enterprise and UHNW customers only
              </p>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
}