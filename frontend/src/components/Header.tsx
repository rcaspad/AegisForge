'use client';

import { useState } from 'react';
import { Menu, X, Zap, Github, Twitter, MessageSquare } from 'lucide-react';
import Link from 'next/link';

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigation = [
    { name: 'Home', href: '/' },
    { name: 'Platform', href: '/platform' },
    { name: 'Documentation', href: '/docs' },
    { name: 'Pricing', href: '/pricing' },
    { name: 'About', href: '/about' },
  ];

  const socialLinks = [
    { name: 'GitHub', href: '#', icon: Github },
    { name: 'Twitter', href: '#', icon: Twitter },
    { name: 'Discord', href: '#', icon: MessageSquare },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-zinc-950/80 backdrop-blur-md border-b border-zinc-800">
      <nav className="mx-auto max-w-7xl px-6 lg:px-8" aria-label="Global">
        <div className="flex items-center justify-between py-4">
          {/* Logo */}
          <div className="flex lg:flex-1">
            <Link href="/" className="-m-1.5 p-1.5 flex items-center gap-2 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-blue-400 flex items-center justify-center transition-transform group-hover:scale-105">
                <Zap className="w-6 h-6 text-white fill-current" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">
                Aegis Forge
              </span>
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="flex lg:hidden">
            <button
              type="button"
              className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-zinc-400 hover:text-white transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <span className="sr-only">Toggle menu</span>
              {mobileMenuOpen ? (
                <X className="h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>

          {/* Desktop navigation */}
          <div className="hidden lg:flex lg:gap-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="text-sm font-semibold leading-6 text-zinc-300 hover:text-white transition-colors relative group"
              >
                {item.name}
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-500 transition-all group-hover:w-full" />
              </Link>
            ))}
          </div>

          {/* CTA & Social Links */}
          <div className="hidden lg:flex lg:flex-1 lg:justify-end lg:gap-x-4 items-center">
            {socialLinks.map((social) => (
              <a
                key={social.name}
                href={social.href}
                className="text-zinc-400 hover:text-white transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <span className="sr-only">{social.name}</span>
                <social.icon className="h-5 w-5" />
              </a>
            ))}
            <Link
              href="/platform"
              className="ml-4 rounded-full bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 transition-all hover:scale-105"
            >
              Launch Platform
            </Link>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden pb-4">
            <div className="space-y-2 py-4">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className="block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-zinc-300 hover:bg-zinc-900 hover:text-white transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
            </div>
            <div className="border-t border-zinc-800 pt-4">
              <Link
                href="/platform"
                className="block w-full rounded-full bg-blue-600 px-6 py-2.5 text-center text-sm font-semibold text-white shadow-sm hover:bg-blue-500 transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Launch Platform
              </Link>
              <div className="flex gap-4 mt-4 justify-center">
                {socialLinks.map((social) => (
                  <a
                    key={social.name}
                    href={social.href}
                    className="text-zinc-400 hover:text-white transition-colors"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <social.icon className="h-5 w-5" />
                  </a>
                ))}
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
