"use client"

// Force fresh build - v2.0
import React, { useEffect, useState } from "react"
import Image from "next/image"
import { cn } from "@/lib/utils"

interface HeroVillainLoadingProps {
  progress: number
  className?: string
}

function HeroVillainLoading({ progress, className }: HeroVillainLoadingProps) {
  const [showImpact, setShowImpact] = useState(false)
  const [showFinalClash, setShowFinalClash] = useState(false)
  const [showFinalImpact, setShowFinalImpact] = useState(false)
  const [heroImageLoaded, setHeroImageLoaded] = useState(false)
  const [villainImageLoaded, setVillainImageLoaded] = useState(false)
  const [imageLoadAttempted, setImageLoadAttempted] = useState(false)
  const [imagesPreloaded, setImagesPreloaded] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // Check if mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 640)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Preload images on component mount
  useEffect(() => {
    const preloadImages = () => {
      const heroImg = new Image()
      const villainImg = new Image()

      heroImg.onload = () => setHeroImageLoaded(true)
      villainImg.onload = () => setVillainImageLoaded(true)

      heroImg.onerror = () => setHeroImageLoaded(false)
      villainImg.onerror = () => setVillainImageLoaded(false)

      heroImg.src = '/hero.png'
      villainImg.src = '/villain.png'

      setImagesPreloaded(true)
    }

    preloadImages()
  }, [])

  // Trigger impact flash when characters are close (around 95-100% progress)
  useEffect(() => {
    if (progress >= 98 && progress <= 100) {
      setShowImpact(true)
      const timer = setTimeout(() => setShowImpact(false), 300)
      return () => clearTimeout(timer)
    }
  }, [progress])

  // Trigger final clash animation when complete
  useEffect(() => {
    if (progress >= 100) {
      setShowFinalClash(true)
      // Show final impact effect immediately at 100%
      const impactTimer = setTimeout(() => setShowFinalImpact(true), 100)
      const clashTimer = setTimeout(() => setShowFinalClash(false), 2000)
      const impactEndTimer = setTimeout(() => setShowFinalImpact(false), 1500)
      return () => {
        clearTimeout(impactTimer)
        clearTimeout(clashTimer)
        clearTimeout(impactEndTimer)
      }
    }
  }, [progress])

  // Calculate character positions (they move closer as progress increases)
  // Reduce movement on mobile to prevent overlap
  const maxMovement = isMobile ? 25 : 40
  const heroPosition = Math.min(progress * 0.4, maxMovement) // Hero moves from 0% to maxMovement%
  const villainPosition = Math.min(progress * 0.4, maxMovement) // Villain moves from 0% to maxMovement% (from right)

  return (
    <div className={cn("relative w-full h-32 sm:h-48 overflow-hidden", className)}>
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-900/20 via-purple-900/30 to-red-900/20 backdrop-blur-sm rounded-2xl" />
      
      {/* Hero Character (Left side) */}
      <div
        className={`absolute bottom-4 sm:bottom-8 transition-all duration-500 ease-out transform ${
          progress > 90 ? 'animate-bounce' : ''
        } ${showFinalClash ? 'scale-110' : ''}`}
        style={{ left: `${heroPosition}%` }}
      >
        <div className="relative">
          {/* Hero PNG Image */}
          <div className="relative w-12 h-16 sm:w-20 sm:h-24 flex items-center justify-center">
            <Image
              src="/hero.png"
              alt="Hero"
              width={80}
              height={96}
              className={`object-contain w-full h-full transition-opacity duration-300 ${
                heroImageLoaded ? 'opacity-100 z-10' : 'opacity-0 z-0'
              }`}
              priority
              onLoad={() => setHeroImageLoaded(true)}
              onError={(e) => {
                console.log('Hero image failed to load:', e);
                setHeroImageLoaded(false);
              }}
            />
            {/* Fallback hero silhouette */}
            <div className={`absolute inset-0 w-10 h-14 sm:w-16 sm:h-20 bg-gradient-to-t from-blue-600 to-cyan-400 rounded-t-full shadow-2xl shadow-blue-500/50 transition-opacity duration-300 ${
              heroImageLoaded ? 'opacity-0 z-0' : 'opacity-100 z-10'
            }`}>
              <div className="absolute -top-1 -left-1 sm:-top-2 sm:-left-2 w-3 h-8 sm:w-6 sm:h-16 bg-gradient-to-b from-red-500 to-red-700 rounded-l-full transform -rotate-12 shadow-lg" />
              <div className="absolute top-4 left-1 sm:top-8 sm:left-2 w-8 h-4 sm:w-12 sm:h-8 bg-gradient-to-b from-blue-500 to-blue-700 rounded-sm" />
              <div className="absolute top-0 left-2 sm:left-4 w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-b from-yellow-200 to-yellow-400 rounded-full border-2 border-blue-600" />
            </div>
            {/* Power aura with intensity based on progress */}
            <div className={`absolute inset-0 bg-blue-400/20 rounded-full blur-sm animate-pulse ${
              progress > 50 ? 'bg-blue-400/40' : ''
            } ${progress > 80 ? 'bg-blue-400/60' : ''}`} />
            {/* Additional glow effect */}
            <div className={`absolute inset-0 bg-cyan-300/10 rounded-full blur-md transition-opacity duration-300 ${
              progress > 70 ? 'opacity-100 animate-pulse' : 'opacity-0'
            }`} />
          </div>
          
          {/* Hero label */}
          <div className="absolute -bottom-4 sm:-bottom-6 left-1/2 transform -translate-x-1/2">
            <span className="text-xs font-bold text-blue-300 bg-blue-900/50 px-2 py-1 rounded-full backdrop-blur-sm">
              HERO
            </span>
          </div>
        </div>
      </div>

      {/* Villain Character (Right side) */}
      <div
        className={`absolute bottom-4 sm:bottom-8 transition-all duration-500 ease-out transform ${
          progress > 90 ? 'animate-bounce' : ''
        } ${showFinalClash ? 'scale-110' : ''}`}
        style={{ right: `${villainPosition}%` }}
      >
        <div className="relative">
          {/* Villain PNG Image */}
          <div className="relative w-12 h-16 sm:w-20 sm:h-24 flex items-center justify-center">
            <Image
              src="/villain.png"
              alt="Villain"
              width={80}
              height={96}
              className={`object-contain w-full h-full transition-opacity duration-300 ${
                villainImageLoaded ? 'opacity-100 z-10' : 'opacity-0 z-0'
              }`}
              priority
              onLoad={() => setVillainImageLoaded(true)}
              onError={(e) => {
                console.log('Villain image failed to load:', e);
                setVillainImageLoaded(false);
              }}
            />
            {/* Fallback villain silhouette */}
            <div className={`absolute inset-0 w-10 h-14 sm:w-16 sm:h-20 bg-gradient-to-t from-gray-800 to-gray-600 rounded-t-full shadow-2xl shadow-purple-500/50 transition-opacity duration-300 ${
              villainImageLoaded ? 'opacity-0 z-0' : 'opacity-100 z-10'
            }`}>
              <div className="absolute -top-1 -right-1 sm:-top-2 sm:-right-2 w-3 h-8 sm:w-6 sm:h-16 bg-gradient-to-b from-purple-800 to-black rounded-r-full transform rotate-12 shadow-lg" />
              <div className="absolute top-4 left-1 sm:top-8 sm:left-2 w-8 h-4 sm:w-12 sm:h-8 bg-gradient-to-b from-gray-700 to-black rounded-sm" />
              <div className="absolute top-0 left-2 sm:left-4 w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-b from-gray-900 to-black rounded-full border-2 border-red-600" />
            </div>
            {/* Dark aura with intensity based on progress */}
            <div className={`absolute inset-0 bg-purple-600/20 rounded-full blur-sm animate-pulse ${
              progress > 50 ? 'bg-purple-600/40' : ''
            } ${progress > 80 ? 'bg-purple-600/60' : ''}`} />
            {/* Additional dark glow effect */}
            <div className={`absolute inset-0 bg-red-500/10 rounded-full blur-md transition-opacity duration-300 ${
              progress > 70 ? 'opacity-100 animate-pulse' : 'opacity-0'
            }`} />
          </div>
          
          {/* Villain label */}
          <div className="absolute -bottom-4 sm:-bottom-6 left-1/2 transform -translate-x-1/2">
            <span className="text-xs font-bold text-purple-300 bg-purple-900/50 px-2 py-1 rounded-full backdrop-blur-sm">
              VILLAIN
            </span>
          </div>
        </div>
      </div>

      {/* Loading Bar Container */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-4/5 h-6">
        {/* Bar background */}
        <div className="w-full h-full bg-white/10 backdrop-blur-sm border border-white/20 rounded-full overflow-hidden shadow-lg">
          {/* Progress fill with gradient */}
          <div 
            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-red-500 transition-all duration-300 ease-out relative"
            style={{ width: `${progress}%` }}
          >
            {/* Animated shine effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse" />
          </div>
        </div>
        
        {/* Progress percentage */}
        <div className="absolute -top-8 left-1/2 transform -translate-x-1/2">
          <span className="text-sm font-bold text-white bg-black/30 px-3 py-1 rounded-full backdrop-blur-sm">
            {Math.round(progress)}%
          </span>
        </div>
      </div>

      {/* Impact Flash Effect */}
      {showImpact && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-32 h-32 bg-white rounded-full opacity-80 animate-ping" />
          <div className="absolute w-24 h-24 bg-yellow-300 rounded-full opacity-60 animate-ping animation-delay-100" />
          <div className="absolute w-16 h-16 bg-orange-400 rounded-full opacity-40 animate-ping animation-delay-200" />
        </div>
      )}

      {/* Final Clash Effect */}
      {showFinalClash && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-48 h-48 bg-gradient-to-r from-blue-400 via-white to-purple-400 rounded-full opacity-90 animate-pulse" />
          <div className="absolute w-32 h-32 bg-gradient-to-r from-yellow-300 to-orange-400 rounded-full opacity-70 animate-ping" />
          <div className="absolute w-16 h-16 bg-white rounded-full opacity-100 animate-bounce" />
          {/* Victory text */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <span className="text-2xl font-bold text-white drop-shadow-lg animate-pulse">
              ANALYSIS COMPLETE!
            </span>
          </div>
        </div>
      )}

      {/* Epic Final Impact Effect at 100% */}
      {showFinalImpact && (
        <div className="absolute inset-0 flex items-center justify-center z-50">
          {/* Massive explosion rings */}
          <div className="w-48 h-48 sm:w-96 sm:h-96 bg-gradient-to-r from-yellow-200 via-orange-300 to-red-400 rounded-full opacity-80 animate-ping" />
          <div className="absolute w-40 h-40 sm:w-80 sm:h-80 bg-gradient-to-r from-blue-300 via-purple-300 to-pink-300 rounded-full opacity-60 animate-ping animation-delay-100" />
          <div className="absolute w-32 h-32 sm:w-64 sm:h-64 bg-gradient-to-r from-white via-yellow-200 to-orange-200 rounded-full opacity-90 animate-ping animation-delay-200" />
          <div className="absolute w-24 h-24 sm:w-48 sm:h-48 bg-white rounded-full opacity-100 animate-pulse" />

          {/* Lightning bolts */}
          <div className="absolute w-1 h-16 sm:h-32 bg-white opacity-100 animate-pulse transform rotate-45" />
          <div className="absolute w-1 h-16 sm:h-32 bg-white opacity-100 animate-pulse transform -rotate-45" />
          <div className="absolute w-1 h-16 sm:h-32 bg-white opacity-100 animate-pulse transform rotate-90" />
          <div className="absolute w-1 h-16 sm:h-32 bg-white opacity-100 animate-pulse" />

          {/* Sparks */}
          <div className="absolute w-2 h-2 bg-yellow-300 rounded-full animate-ping top-8 left-8" />
          <div className="absolute w-2 h-2 bg-orange-400 rounded-full animate-ping top-8 right-8 animation-delay-100" />
          <div className="absolute w-2 h-2 bg-red-400 rounded-full animate-ping bottom-8 left-8 animation-delay-200" />
          <div className="absolute w-2 h-2 bg-purple-400 rounded-full animate-ping bottom-8 right-8 animation-delay-300" />

          {/* Epic victory text */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="text-center">
              <span className="text-2xl sm:text-4xl font-black text-white drop-shadow-2xl animate-bounce">
                💥 EPIC CLASH! 💥
              </span>
              <div className="mt-2">
                <span className="text-sm sm:text-lg font-bold text-yellow-200 drop-shadow-lg animate-pulse">
                  Heroes vs Villains Analysis Complete!
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Energy crackling effects when characters are close */}
      {progress > 70 && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="w-2 h-16 bg-gradient-to-t from-blue-400 to-purple-400 opacity-60 animate-pulse transform rotate-12" />
          <div className="absolute w-2 h-12 bg-gradient-to-t from-purple-400 to-red-400 opacity-40 animate-pulse transform -rotate-12 left-4" />
          <div className="absolute w-1 h-8 bg-white opacity-80 animate-pulse transform rotate-45 left-2 top-2" />
        </div>
      )}

      {/* Loading text */}
      <div className="absolute top-2 sm:top-4 left-1/2 transform -translate-x-1/2">
        <div className="flex items-center gap-2 bg-black/30 backdrop-blur-sm px-3 sm:px-4 py-1 sm:py-2 rounded-full border border-white/20">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
          <span className="text-xs sm:text-sm font-medium text-white">
            {progress < 30 ? "Analyzing comic..." :
             progress < 60 ? "Processing image..." :
             progress < 90 ? "Fetching market data..." :
             "Almost ready!"}
          </span>
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse animation-delay-300" />
        </div>

      </div>
    </div>
  )
}

export default HeroVillainLoading
