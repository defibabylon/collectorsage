"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import {
  Upload,
  ImageIcon,
  TrendingUp,
  Shield,
  Zap,
  BarChart3,
  Star,
  Calendar,
  DollarSign,
  Award,
  Sparkles,
  Eye,
  Brain,
  Target,
} from "lucide-react"
import Image from "next/image"

interface ComicValuation {
  title: string
  issueNumber: string
  year: number
  publisher: string
  ratings: {
    impact: number
    rarity: number
    value: number
    story: number
    artwork: number
  }
  prices: {
    graded: {
      grade: string
      price: number
    }[]
    nonGraded: {
      condition: string
      price: number
    }[]
  }
  imageUrl: string
}

export default function CollectorSage() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [valuation, setValuation] = useState<ComicValuation | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file: File) => {
    if (!file.type.startsWith("image/")) {
      setError("Please upload an image file")
      return
    }

    setError(null)
    setUploadedFile(file)
    setIsAnalyzing(true)

    // Simulate AI analysis
    setTimeout(() => {
      const mockValuation: ComicValuation = {
        title: "The Amazing Spider-Man",
        issueNumber: "#121",
        year: 1973,
        publisher: "Marvel Comics",
        ratings: {
          impact: 85,
          rarity: 72,
          value: 78,
          story: 88,
          artwork: 82,
        },
        prices: {
          graded: [
            { grade: "CGC 9.8", price: 1250 },
            { grade: "CGC 9.6", price: 850 },
            { grade: "CGC 9.4", price: 650 },
            { grade: "CGC 9.0", price: 450 },
          ],
          nonGraded: [
            { condition: "Near Mint", price: 380 },
            { condition: "Very Fine", price: 220 },
            { condition: "Fine", price: 120 },
            { condition: "Good", price: 65 },
          ],
        },
        imageUrl: URL.createObjectURL(file),
      }

      setValuation(mockValuation)
      setIsAnalyzing(false)
    }, 3000)
  }

  const getRatingColor = (rating: number) => {
    if (rating >= 80) return "from-emerald-400 to-teal-500"
    if (rating >= 60) return "from-amber-400 to-orange-500"
    return "from-red-400 to-pink-500"
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-cyan-500/20 to-blue-600/20 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-purple-500/10 to-pink-600/10 rounded-full blur-3xl animate-pulse delay-500" />
      </div>

      {/* Hero Section */}
      <section className="relative z-10 overflow-hidden">
        <div className="container mx-auto px-4 py-24 text-center">
          <div className="max-w-5xl mx-auto">
            {/* Floating Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 backdrop-blur-sm border border-white/10 mb-8">
              <Sparkles className="h-4 w-4 text-blue-400" />
              <span className="text-sm text-blue-200 font-medium">AI-Powered Valuation Engine</span>
            </div>

            <h1 className="text-7xl md:text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-200 to-purple-300 mb-6 tracking-tight leading-none">
              COLLECTOR
              <span className="block text-6xl md:text-8xl bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                SAGE
              </span>
            </h1>

            <div className="relative">
              <p className="text-2xl md:text-3xl text-blue-200/80 mb-8 font-light tracking-wide">
                AI-POWERED COMIC BOOK VALUATION
              </p>
              <div className="absolute -inset-4 bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-xl rounded-full" />
            </div>

            <p className="text-lg text-gray-300/80 max-w-2xl mx-auto leading-relaxed mb-12">
              Discover the true value of your comic collection with cutting-edge AI technology. Get instant, accurate
              valuations backed by comprehensive market analysis.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button className="group relative px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold rounded-2xl shadow-2xl shadow-blue-500/25 transition-all duration-300 hover:scale-105">
                <span className="relative z-10 flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Start Analyzing
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-2xl blur opacity-0 group-hover:opacity-50 transition-opacity duration-300" />
              </Button>

              <Button
                variant="outline"
                className="px-8 py-4 bg-white/5 backdrop-blur-sm border-white/20 text-white hover:bg-white/10 rounded-2xl font-semibold transition-all duration-300 hover:scale-105"
              >
                <Eye className="h-5 w-5 mr-2" />
                View Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Upload Section */}
      <section className="relative z-10 py-20 px-4">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 backdrop-blur-sm border border-white/10 mb-6">
              <Upload className="h-4 w-4 text-emerald-400" />
              <span className="text-sm text-emerald-200 font-medium">Upload & Analyze</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Upload Your Comic</h2>
            <p className="text-gray-300/80 text-xl">
              Take a clear photo of your comic book cover for instant AI analysis
            </p>
          </div>

          <div className="relative">
            {/* Glassmorphism Card */}
            <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
              <div
                className={`relative border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 ${
                  dragActive
                    ? "border-blue-400/50 bg-gradient-to-br from-blue-500/10 to-purple-500/10 scale-105"
                    : "border-white/20 hover:border-white/30 hover:bg-white/5"
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {/* Upload Icon with Gradient */}
                <div className="relative mb-6">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full blur-xl opacity-50" />
                  <div className="relative bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-full w-fit mx-auto">
                    <Upload className="h-12 w-12 text-white" />
                  </div>
                </div>

                <h3 className="text-2xl font-bold text-white mb-3">Drop your comic image here</h3>
                <p className="text-gray-300/80 mb-8 text-lg">or click to browse your files</p>

                <input type="file" accept="image/*" onChange={handleFileInput} className="hidden" id="file-upload" />
                <label htmlFor="file-upload">
                  <Button className="group relative px-10 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold rounded-2xl shadow-2xl shadow-cyan-500/25 transition-all duration-300 hover:scale-105">
                    <span className="relative z-10 flex items-center gap-3">
                      <ImageIcon className="h-6 w-6" />
                      Select Image
                    </span>
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-300 to-blue-400 rounded-2xl blur opacity-0 group-hover:opacity-50 transition-opacity duration-300" />
                  </Button>
                </label>

                {/* Supported formats */}
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {["JPG", "PNG", "WEBP", "HEIC"].map((format) => (
                    <Badge key={format} variant="outline" className="border-white/20 text-white/60 bg-white/5">
                      {format}
                    </Badge>
                  ))}
                </div>
              </div>

              {error && (
                <div className="mt-6 p-4 bg-gradient-to-r from-red-500/10 to-pink-500/10 backdrop-blur-sm border border-red-500/20 rounded-2xl">
                  <p className="text-red-200 text-center font-medium">{error}</p>
                </div>
              )}

              {isAnalyzing && (
                <div className="mt-8 space-y-6">
                  <div className="text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 backdrop-blur-sm border border-white/10 mb-4">
                      <Brain className="h-4 w-4 text-blue-400 animate-pulse" />
                      <span className="text-sm text-blue-200 font-medium">AI Processing</span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">Analyzing your comic...</h3>
                    <p className="text-gray-300/80">Our AI is examining the image and cross-referencing market data</p>
                  </div>
                  <div className="relative">
                    <Progress value={66} className="w-full h-3 bg-white/10" />
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full blur opacity-50" />
                  </div>
                </div>
              )}
            </div>

            {/* Decorative Elements */}
            <div className="absolute -top-4 -right-4 w-8 h-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full blur-sm opacity-60" />
            <div className="absolute -bottom-4 -left-4 w-6 h-6 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full blur-sm opacity-60" />
          </div>
        </div>
      </section>

      {/* Results Section */}
      {valuation && (
        <section className="relative z-10 py-20 px-4">
          <div className="container mx-auto max-w-7xl">
            <div className="text-center mb-16">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-emerald-500/10 to-teal-500/10 backdrop-blur-sm border border-white/10 mb-6">
                <Target className="h-4 w-4 text-emerald-400" />
                <span className="text-sm text-emerald-200 font-medium">Analysis Complete</span>
              </div>
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Valuation Results</h2>
              <p className="text-gray-300/80 text-xl">Comprehensive AI-powered analysis of your comic book</p>
            </div>

            <div className="grid lg:grid-cols-2 gap-8 mb-12">
              {/* Comic Image - Enhanced */}
              <div className="relative">
                <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-2xl">
                  <div className="aspect-[3/4] relative rounded-2xl overflow-hidden bg-gradient-to-br from-slate-800 to-slate-900">
                    <Image
                      src={valuation.imageUrl || "/placeholder.svg"}
                      alt="Comic cover"
                      fill
                      className="object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
                  </div>

                  {/* Floating Stats */}
                  <div className="absolute -top-3 -right-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-4 py-2 rounded-full text-sm font-bold shadow-lg">
                    AI Verified ✓
                  </div>
                </div>

                {/* Decorative glow */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-3xl blur-2xl -z-10" />
              </div>

              {/* Comic Details - Enhanced */}
              <div className="space-y-6">
                {/* Main Details Card */}
                <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl">
                      <Award className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-white">Comic Details</h3>
                  </div>

                  <div className="space-y-4">
                    <h4 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-blue-200">
                      {valuation.title} {valuation.issueNumber}
                    </h4>
                    <div className="flex flex-wrap gap-3">
                      <Badge className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                        <Calendar className="h-4 w-4 mr-2" />
                        {valuation.year}
                      </Badge>
                      <Badge className="bg-white/10 backdrop-blur-sm border-white/20 text-white px-4 py-2 rounded-full text-sm font-semibold">
                        {valuation.publisher}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Ratings Card - Enhanced */}
                <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl">
                      <BarChart3 className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-white">Quality Ratings</h3>
                  </div>

                  <div className="space-y-6">
                    {Object.entries(valuation.ratings).map(([key, value]) => (
                      <div key={key} className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-200 capitalize font-semibold text-lg">{key}</span>
                          <span className="text-white font-bold text-xl">{value}/100</span>
                        </div>
                        <div className="relative w-full bg-white/10 rounded-full h-3 overflow-hidden">
                          <div
                            className={`h-3 rounded-full bg-gradient-to-r ${getRatingColor(value)} transition-all duration-1000 ease-out relative`}
                            style={{ width: `${value}%` }}
                          >
                            <div className="absolute inset-0 bg-white/20 rounded-full blur-sm" />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Price Estimates - Enhanced */}
            <div className="grid md:grid-cols-2 gap-8">
              {/* Graded Prices */}
              <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 bg-gradient-to-r from-amber-500 to-orange-600 rounded-2xl">
                    <Shield className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">Graded Comics</h3>
                    <p className="text-gray-300/80">Professional grading service valuations</p>
                  </div>
                </div>

                <div className="space-y-4">
                  {valuation.prices.graded.map((price, index) => (
                    <div
                      key={index}
                      className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-4 hover:bg-white/10 transition-all duration-300"
                    >
                      <div className="flex justify-between items-center">
                        <span className="text-gray-200 font-semibold">{price.grade}</span>
                        <span className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-500">
                          £{price.price.toLocaleString()}
                        </span>
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 to-teal-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </div>
                  ))}
                </div>
              </div>

              {/* Non-Graded Prices */}
              <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl">
                    <DollarSign className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">Raw Comics</h3>
                    <p className="text-gray-300/80">Ungraded comic book valuations</p>
                  </div>
                </div>

                <div className="space-y-4">
                  {valuation.prices.nonGraded.map((price, index) => (
                    <div
                      key={index}
                      className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-4 hover:bg-white/10 transition-all duration-300"
                    >
                      <div className="flex justify-between items-center">
                        <span className="text-gray-200 font-semibold">{price.condition}</span>
                        <span className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                          £{price.price.toLocaleString()}
                        </span>
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-blue-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Features Section - Enhanced */}
      <section className="relative z-10 py-20 px-4">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-purple-500/10 to-pink-500/10 backdrop-blur-sm border border-white/10 mb-6">
              <Sparkles className="h-4 w-4 text-purple-400" />
              <span className="text-sm text-purple-200 font-medium">Why Choose Us</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Why Choose{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                CollectorSage?
              </span>
            </h2>
            <p className="text-gray-300/80 text-xl max-w-3xl mx-auto">
              Advanced AI technology meets comprehensive market analysis to deliver the most accurate comic book
              valuations available.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: Zap,
                title: "AI-Powered Recognition",
                description: "Advanced computer vision identifies comics with 99%+ accuracy",
                gradient: "from-yellow-400 to-orange-500",
              },
              {
                icon: TrendingUp,
                title: "Market Analysis",
                description: "Real-time pricing from multiple auction houses and dealers",
                gradient: "from-green-400 to-emerald-500",
              },
              {
                icon: BarChart3,
                title: "Detailed Reports",
                description: "Comprehensive valuations with quality ratings and insights",
                gradient: "from-blue-400 to-cyan-500",
              },
              {
                icon: Star,
                title: "Historical Trends",
                description: "Track price movements and market trends over time",
                gradient: "from-purple-400 to-pink-500",
              },
            ].map((feature, index) => (
              <div key={index} className="group relative">
                <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 text-center shadow-2xl hover:bg-white/10 transition-all duration-300 hover:scale-105">
                  <div
                    className={`inline-flex p-4 bg-gradient-to-r ${feature.gradient} rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300`}
                  >
                    <feature.icon className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                  <p className="text-gray-300/80 leading-relaxed">{feature.description}</p>
                </div>
                <div
                  className={`absolute inset-0 bg-gradient-to-r ${feature.gradient} rounded-3xl blur-xl opacity-0 group-hover:opacity-20 transition-opacity duration-300 -z-10`}
                />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer - Enhanced */}
      <footer className="relative z-10 py-16 px-4 border-t border-white/10">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center">
            <h3 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-200 to-purple-300 mb-4">
              COLLECTOR
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">SAGE</span>
            </h3>
            <p className="text-gray-300/80 mb-8 text-lg">The future of comic book valuation is here</p>
            <div className="flex justify-center items-center space-x-6 text-sm text-gray-400">
              <span>© 2024 CollectorSage</span>
              <div className="w-1 h-1 bg-gray-500 rounded-full" />
              <span className="hover:text-white transition-colors cursor-pointer">Privacy Policy</span>
              <div className="w-1 h-1 bg-gray-500 rounded-full" />
              <span className="hover:text-white transition-colors cursor-pointer">Terms of Service</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
