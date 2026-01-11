'use client';

import { useState, useRef, ChangeEvent } from 'react';
import { Upload, X, Play, Image as ImageIcon, Video, FileText, Zap, ArrowRight } from 'lucide-react';
import Link from 'next/link';

interface MediaFile {
  id: string;
  file: File;
  preview: string;
  type: 'image' | 'video';
}

export default function Hero() {
  const [mediaFiles, setMediaFiles] = useState<MediaFile[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;

    const newFiles = Array.from(files)
      .filter(file => file.type.startsWith('image/') || file.type.startsWith('video/'))
      .map(file => ({
        id: Math.random().toString(36).substr(2, 9),
        file,
        preview: URL.createObjectURL(file),
        type: file.type.startsWith('image/') ? 'image' as const : 'video' as const,
      }));

    setMediaFiles(prev => [...prev, ...newFiles]);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files);
    }
  };

  const removeFile = (id: string) => {
    setMediaFiles(prev => {
      const file = prev.find(f => f.id === id);
      if (file) {
        URL.revokeObjectURL(file.preview);
      }
      return prev.filter(f => f.id !== id);
    });
  };

  return (
    <div className="relative isolate overflow-hidden bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 pt-24 pb-16">
      {/* Background effects */}
      <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
        <div
          className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-blue-600 to-blue-400 opacity-20 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
          style={{
            clipPath: 'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)',
          }}
        />
      </div>

      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          {/* Badge */}
          <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-1.5 text-sm text-blue-400 backdrop-blur-sm">
            <Zap className="w-4 h-4 fill-current" />
            <span className="font-semibold">Autonomous Software Engineering</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl font-bold tracking-tight text-white sm:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-white to-zinc-400">
            Build Production Software with{' '}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-blue-600">
              Natural Language
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mt-6 text-lg leading-8 text-zinc-400 max-w-2xl mx-auto">
            Aegis Forge is an autonomous development platform that transforms your ideas into production-ready software. 
            Multi-agent AI system handles architecture, coding, security, and deployment—automatically.
          </p>

          {/* CTA Buttons */}
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link
              href="/platform"
              className="group rounded-full bg-blue-600 px-8 py-3.5 text-base font-semibold text-white shadow-lg hover:bg-blue-500 transition-all hover:scale-105 flex items-center gap-2"
            >
              Start Building
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/docs"
              className="rounded-full border border-zinc-700 bg-zinc-900/50 px-8 py-3.5 text-base font-semibold text-zinc-200 hover:bg-zinc-800 hover:border-zinc-600 transition-all backdrop-blur-sm"
            >
              View Docs
            </Link>
          </div>

          {/* Media Upload Section */}
          <div className="mt-16">
            <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">
              Showcase Your Vision
            </h3>
            
            {/* Upload Zone */}
            <div
              className={`relative border-2 border-dashed rounded-2xl p-8 transition-all ${
                dragActive 
                  ? 'border-blue-500 bg-blue-500/5' 
                  : 'border-zinc-800 bg-zinc-900/30 hover:border-zinc-700'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                multiple
                accept="image/*,video/*"
                onChange={handleChange}
              />

              <div className="flex flex-col items-center gap-4">
                <div className="p-4 rounded-full bg-zinc-800/50 border border-zinc-700">
                  <Upload className="w-8 h-8 text-zinc-400" />
                </div>
                
                <div className="text-center">
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="text-blue-400 hover:text-blue-300 font-semibold transition-colors"
                  >
                    Click to upload
                  </button>
                  <span className="text-zinc-500"> or drag and drop</span>
                  <p className="text-sm text-zinc-600 mt-1">
                    Images or videos up to 50MB
                  </p>
                </div>
              </div>
            </div>

            {/* Media Preview Grid */}
            {mediaFiles.length > 0 && (
              <div className="mt-6 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {mediaFiles.map((media) => (
                  <div
                    key={media.id}
                    className="relative group aspect-square rounded-lg overflow-hidden bg-zinc-900 border border-zinc-800"
                  >
                    {media.type === 'image' ? (
                      <img
                        src={media.preview}
                        alt="Upload preview"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="relative w-full h-full">
                        <video
                          src={media.preview}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 flex items-center justify-center bg-black/30">
                          <Play className="w-10 h-10 text-white/80" />
                        </div>
                      </div>
                    )}

                    {/* File type indicator */}
                    <div className="absolute top-2 left-2 p-1.5 rounded-md bg-zinc-950/80 backdrop-blur-sm">
                      {media.type === 'image' ? (
                        <ImageIcon className="w-4 h-4 text-zinc-400" />
                      ) : (
                        <Video className="w-4 h-4 text-zinc-400" />
                      )}
                    </div>

                    {/* Remove button */}
                    <button
                      onClick={() => removeFile(media.id)}
                      className="absolute top-2 right-2 p-1.5 rounded-md bg-red-600/90 hover:bg-red-500 transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <X className="w-4 h-4 text-white" />
                    </button>

                    {/* File info overlay */}
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <p className="text-xs text-zinc-300 truncate">
                        {media.file.name}
                      </p>
                      <p className="text-xs text-zinc-500">
                        {(media.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Upload status */}
            {mediaFiles.length > 0 && (
              <div className="mt-4 flex items-center justify-between text-sm text-zinc-500">
                <span>{mediaFiles.length} file{mediaFiles.length !== 1 ? 's' : ''} uploaded</span>
                <button
                  onClick={() => {
                    mediaFiles.forEach(f => URL.revokeObjectURL(f.preview));
                    setMediaFiles([]);
                  }}
                  className="text-red-400 hover:text-red-300 transition-colors"
                >
                  Clear all
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Features Grid */}
        <div className="mx-auto mt-24 max-w-5xl">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
            <div className="relative rounded-2xl border border-zinc-800 bg-zinc-900/30 p-6 backdrop-blur-sm">
              <div className="mb-4 p-3 rounded-xl bg-blue-600/10 w-fit">
                <Zap className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Multi-Agent System</h3>
              <p className="text-sm text-zinc-400">
                Six specialized AI agents work together—from product vision to deployment.
              </p>
            </div>

            <div className="relative rounded-2xl border border-zinc-800 bg-zinc-900/30 p-6 backdrop-blur-sm">
              <div className="mb-4 p-3 rounded-xl bg-green-600/10 w-fit">
                <FileText className="w-6 h-6 text-green-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">SOC2 Compliant</h3>
              <p className="text-sm text-zinc-400">
                Security auditor agent ensures production-grade code with zero trust architecture.
              </p>
            </div>

            <div className="relative rounded-2xl border border-zinc-800 bg-zinc-900/30 p-6 backdrop-blur-sm">
              <div className="mb-4 p-3 rounded-xl bg-purple-600/10 w-fit">
                <Upload className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Self-Healing</h3>
              <p className="text-sm text-zinc-400">
                System learns from errors and creates "vaccines" to prevent recurring issues.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom gradient */}
      <div className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]">
        <div
          className="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-blue-600 to-blue-400 opacity-20 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]"
          style={{
            clipPath: 'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)',
          }}
        />
      </div>
    </div>
  );
}
