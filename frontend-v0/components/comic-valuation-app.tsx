"use client"

import React, { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import HeroVillainLoading from "./hero-villain-loading"
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
  Clock,
  Database,
} from "lucide-react"
import Image from "next/image"
import axios from "axios"

// API URL configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

interface ComicDetails {
  title: string
  issueNumber: string
  year: string
  min_price: string
  max_price: string
  avg_price: string
  sales_trend: string
  database_avg_price: string
  total_listings: number
}

interface ApiResponse {
  comicDetails: ComicDetails
  report: string
  processingTime: string
  breakdown?: {
    image_processing?: string
    database_fetch?: string
    ebay_fetch?: string
    parallel_fetch?: string
  }
}

export default function ComicValuationApp() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<ApiResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [progress, setProgress] = useState(0)

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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
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
    setProgress(0)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('image', file)

      // Progress simulation
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90))
      }, 500)

      // Try fast endpoint first, fallback to regular if needed
      let response
      try {
        response = await axios.post(`${API_URL}/process_image_fast`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
      } catch (fastError) {
        console.log('Fast endpoint failed, trying regular endpoint:', fastError)
        response = await axios.post(`${API_URL}/process_image`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
      }

      clearInterval(progressInterval)
      setProgress(100)
      
      setResult(response.data)
      setIsAnalyzing(false)
    } catch (error) {
      console.error('Error processing image:', error)
      setError('Failed to process image. Please try again.')
      setIsAnalyzing(false)
      setProgress(0)
    }
  }

  const resetApp = () => {
    setUploadedFile(null)
    setResult(null)
    setError(null)
    setProgress(0)
    setIsAnalyzing(false)
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
        <div className="container mx-auto px-4 sm:px-6 py-16 sm:py-24 text-center">
          <div className="max-w-5xl mx-auto">
            {/* Floating Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 backdrop-blur-sm border border-white/10 mb-8">
              <Sparkles className="h-4 w-4 text-blue-400" />
              <span className="text-sm text-blue-200 font-medium">AI-Powered Valuation Engine</span>
            </div>

            <h1 className="text-4xl sm:text-6xl md:text-7xl lg:text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-200 to-purple-300 mb-6 tracking-tight leading-none">
              COLLECTOR
              <span className="block text-3xl sm:text-5xl md:text-6xl lg:text-8xl bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                SAGE
              </span>
            </h1>

            <div className="relative">
              <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl text-blue-200/80 mb-8 font-light tracking-wide">
                AI-POWERED COMIC BOOK VALUATION
              </p>
              <div className="absolute -inset-4 bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-xl rounded-full" />
            </div>

            <p className="text-lg text-gray-300/80 max-w-2xl mx-auto leading-relaxed mb-12">
              Discover the true value of your comic collection with cutting-edge AI technology. Get instant, accurate
              valuations backed by comprehensive market analysis.
            </p>

            {/* CTA Buttons */}
            {result && (
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button
                  onClick={resetApp}
                  className="group relative px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold rounded-2xl shadow-2xl shadow-blue-500/25 transition-all duration-300 hover:scale-105"
                >
                  <span className="relative z-10 flex items-center gap-2">
                    <Zap className="h-5 w-5" />
                    Analyze Another Comic
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-2xl blur opacity-0 group-hover:opacity-50 transition-opacity duration-300" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </section>

      {!result ? (
        /* Upload Section */
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
                  {uploadedFile ? (
                    <div className="space-y-4">
                      <div className="relative w-32 h-40 mx-auto rounded-lg overflow-hidden">
                        <Image
                          src={URL.createObjectURL(uploadedFile)}
                          alt="Uploaded comic"
                          fill
                          className="object-cover"
                        />
                      </div>
                      <p className="text-white font-medium">{uploadedFile.name}</p>
                    </div>
                  ) : (
                    <>
                      {/* Upload Icon with Gradient */}
                      <div className="relative mb-6">
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full blur-xl opacity-50" />
                        <div className="relative bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-full w-fit mx-auto">
                          <Upload className="h-12 w-12 text-white" />
                        </div>
                      </div>

                      <h3 className="text-2xl font-bold text-white mb-3">Drop your comic image here</h3>
                      <p className="text-gray-300/80 mb-8 text-lg">or click to browse your files</p>

                      <input type="file" accept="image/*" onChange={handleChange} className="hidden" id="file-upload" />
                      <Button
                        onClick={() => document.getElementById('file-upload')?.click()}
                        className="group relative px-10 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold rounded-2xl shadow-2xl shadow-cyan-500/25 transition-all duration-300 hover:scale-105"
                      >
                        <span className="relative z-10 flex items-center gap-3">
                          <ImageIcon className="h-6 w-6" />
                          Select Image
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-300 to-blue-400 rounded-2xl blur opacity-0 group-hover:opacity-50 transition-opacity duration-300" />
                      </Button>

                      {/* Supported formats */}
                      <div className="mt-6 flex flex-wrap justify-center gap-2">
                        {["JPG", "PNG", "WEBP", "HEIC"].map((format) => (
                          <Badge key={format} variant="outline" className="border-white/20 text-white/60 bg-white/5">
                            {format}
                          </Badge>
                        ))}
                      </div>
                    </>
                  )}
                </div>

                {error && (
                  <div className="mt-6 p-4 bg-gradient-to-r from-red-500/10 to-pink-500/10 backdrop-blur-sm border border-red-500/20 rounded-2xl">
                    <p className="text-red-200 text-center font-medium">{error}</p>
                  </div>
                )}

                {isAnalyzing && (
                  <div className="mt-8">
                    <HeroVillainLoading progress={progress} />
                  </div>
                )}
              </div>

              {/* Decorative Elements */}
              <div className="absolute -top-4 -right-4 w-8 h-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full blur-sm opacity-60" />
              <div className="absolute -bottom-4 -left-4 w-6 h-6 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full blur-sm opacity-60" />
            </div>
          </div>
        </section>
      ) : (
        /* Results Section */
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
                      src={uploadedFile ? URL.createObjectURL(uploadedFile) : "/placeholder.svg"}
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
                <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-4 sm:p-6 md:p-8 shadow-2xl">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl">
                      <Award className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="text-xl sm:text-2xl font-bold text-white">Comic Details</h3>
                  </div>

                  <div className="space-y-4">
                    <h4 className="text-xl sm:text-2xl md:text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-blue-200">
                      {result.comicDetails.title} {result.comicDetails.issueNumber}
                    </h4>
                    <div className="flex flex-wrap gap-3">
                      <Badge className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                        <Calendar className="h-4 w-4 mr-2" />
                        {result.comicDetails.year}
                      </Badge>
                      <Badge className="bg-white/10 backdrop-blur-sm border-white/20 text-white px-4 py-2 rounded-full text-sm font-semibold">
                        <Database className="h-4 w-4 mr-2" />
                        {result.comicDetails.total_listings} listings
                      </Badge>
                      <Badge className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                        <TrendingUp className="h-4 w-4 mr-2" />
                        {result.comicDetails.sales_trend}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Price Analysis Card */}
                <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-4 sm:p-6 md:p-8 shadow-2xl">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl">
                      <DollarSign className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="text-xl sm:text-2xl font-bold text-white">Price Analysis</h3>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-4">
                      <div className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-3 sm:p-4 hover:bg-white/10 transition-all duration-300">
                        <div className="flex justify-between items-center gap-2">
                          <span className="text-gray-200 font-semibold text-sm sm:text-base">Min Price</span>
                          <span className="text-lg sm:text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-pink-500 truncate">
                            £{result.comicDetails.min_price}
                          </span>
                        </div>
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 to-pink-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      </div>
                      <div className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-3 sm:p-4 hover:bg-white/10 transition-all duration-300">
                        <div className="flex justify-between items-center gap-2">
                          <span className="text-gray-200 font-semibold text-sm sm:text-base">Max Price</span>
                          <span className="text-lg sm:text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-500 truncate">
                            £{result.comicDetails.max_price}
                          </span>
                        </div>
                        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 to-teal-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div className="group relative bg-gradient-to-r from-blue-600/20 to-purple-600/20 backdrop-blur-sm border border-blue-500/30 rounded-2xl p-3 sm:p-4 hover:from-blue-600/30 hover:to-purple-600/30 transition-all duration-300">
                        <div className="flex justify-between items-center gap-2">
                          <span className="text-gray-200 font-semibold text-sm sm:text-base">Average Price</span>
                          <span className="text-lg sm:text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 truncate">
                            £{result.comicDetails.avg_price}
                          </span>
                        </div>
                      </div>
                      <div className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-3 sm:p-4 hover:bg-white/10 transition-all duration-300">
                        <div className="flex justify-between items-center gap-2">
                          <span className="text-gray-200 font-semibold text-sm sm:text-base">Database Avg</span>
                          <span className="text-lg sm:text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 truncate">
                            £{result.comicDetails.database_avg_price}
                          </span>
                        </div>
                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-blue-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Analysis Report and Processing Details */}
            <div className="grid md:grid-cols-2 gap-8">
              {/* Detailed Report */}
              <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 bg-gradient-to-r from-amber-500 to-orange-600 rounded-2xl">
                    <BarChart3 className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">Market Analysis</h3>
                    <p className="text-gray-300/80">Detailed insights from our AI analysis</p>
                  </div>
                </div>
                <div className="relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 max-h-64 overflow-y-auto">
                  <div className="text-gray-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {result.report}
                  </div>
                </div>
              </div>

              {/* Processing Information */}
              <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl">
                    <Clock className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">Processing Details</h3>
                    <p className="text-gray-300/80">Analysis performance metrics</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-4 hover:bg-white/10 transition-all duration-300">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-200 flex items-center gap-2 font-semibold">
                        <Zap className="h-4 w-4" />
                        Total Processing Time
                      </span>
                      <span className="text-white font-bold">{result.processingTime}</span>
                    </div>
                  </div>

                  {result.breakdown && (
                    <div className="space-y-3">
                      <h4 className="text-white font-semibold">Processing Breakdown:</h4>
                      {Object.entries(result.breakdown).map(([key, value]) => (
                        <div key={key} className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-3 hover:bg-white/10 transition-all duration-300">
                          <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-300 capitalize">{key.replace('_', ' ')}</span>
                            <span className="text-gray-200 font-mono">{value}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="relative bg-gradient-to-r from-emerald-500/10 to-teal-500/10 backdrop-blur-sm border border-emerald-500/20 rounded-2xl p-4">
                    <div className="flex items-center gap-2 text-emerald-400">
                      <Shield className="h-4 w-4" />
                      <span className="text-sm font-medium">Analysis Complete</span>
                    </div>
                    <p className="text-xs text-emerald-300 mt-1">
                      Data sourced from multiple marketplaces and verified databases
                    </p>
                  </div>
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
            <h3 className="text-2xl sm:text-3xl md:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-200 to-purple-300 mb-4">
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
