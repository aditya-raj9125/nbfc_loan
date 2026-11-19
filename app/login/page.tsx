'use client';

import React, { useState } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  ShieldCheck,
  Zap,
  ArrowRight,
  UserCheck,
  AlertCircle,
  FileText,
  CreditCard,
  User,
  Sparkles,
  Lock,
  Mail,
  ChevronRight
} from 'lucide-react';

const DEMO_ACCOUNTS = [
  {
    name: 'Rahul Sharma',
    email: 'rahul.sharma@email.com',
    tag: 'Instant Approval',
    tagColor: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    icon: Zap,
    description: 'Pre-approved for ₹5,00,000 | CIBIL 782 | Instant sanction demo',
    amount: '₹5,00,000',
    score: 782,
  },
  {
    name: 'Priya Patel',
    email: 'priya.patel@email.com',
    tag: 'Salary Slip Upload',
    tagColor: 'bg-blue-100 text-blue-800 border-blue-200',
    icon: FileText,
    description: 'Pre-approved ₹7.5L | Requests ₹10L | Demonstrates Vision AI payslip review',
    amount: '₹7,50,000',
    score: 820,
  },
  {
    name: 'Vikram Singh',
    email: 'vikram.singh@email.com',
    tag: 'Credit Rejection (<700)',
    tagColor: 'bg-rose-100 text-rose-800 border-rose-200',
    icon: AlertCircle,
    description: 'Credit score 680 < 700 | Demonstrates underwriting policy rejection',
    amount: '₹4,00,000',
    score: 680,
  },
  {
    name: 'Anjali Verma',
    email: 'anjali.verma@email.com',
    tag: 'KYC Incomplete',
    tagColor: 'bg-purple-100 text-purple-800 border-purple-200',
    icon: UserCheck,
    description: 'KYC pending in CRM | Demonstrates Aadhaar & PAN verification flow',
    amount: '₹2,50,000',
    score: 730,
  },
  {
    name: 'Rajesh Gupta',
    email: 'rajesh.gupta@email.com',
    tag: 'High Value HNI',
    tagColor: 'bg-amber-100 text-amber-800 border-amber-200',
    icon: CreditCard,
    description: 'Pre-approved ₹10,00,000 | CIBIL 800 | High net worth borrower',
    amount: '₹10,00,000',
    score: 800,
  },
];

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get('callbackUrl') || '/';

  const [email, setEmail] = useState('rahul.sharma@email.com');
  const [password, setPassword] = useState('password123');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (loginEmail: string) => {
    setIsLoading(true);
    setError('');

    try {
      const res = await signIn('credentials', {
        redirect: false,
        email: loginEmail,
        password: password || 'password123',
        callbackUrl,
      });

      if (res?.error) {
        setError('Login failed. Please check credentials or select a demo account.');
        setIsLoading(false);
      } else {
        router.push(callbackUrl);
        router.refresh();
      }
    } catch (err) {
      setError('An unexpected error occurred during login.');
      setIsLoading(false);
    }
  };

  const handleGuestLogin = async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await signIn('credentials', {
        redirect: false,
        email: 'guest',
        password: 'guest',
        callbackUrl,
      });
      if (!res?.error) {
        router.push(callbackUrl);
        router.refresh();
      } else {
        setError('Guest login failed.');
        setIsLoading(false);
      }
    } catch {
      setError('Guest login failed.');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/40 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Decorative Orbs */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-blue-100/50 rounded-full blur-3xl -z-10 pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-amber-100/40 rounded-full blur-3xl -z-10 pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-2xl px-4">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 border border-blue-200/60 text-blue-700 text-xs font-semibold mb-3 shadow-sm"
          >
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <span>EY Techathon 6.0 Demonstration Portal</span>
          </motion.div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight sm:text-4xl">
            NBFC Finance Limited
          </h1>
          <p className="mt-2 text-sm text-gray-600 max-w-md mx-auto">
            Agentic AI Loan Assistant Platform. Select a pre-seeded test scenario below or sign in as a guest.
          </p>
        </div>

        {/* Main Card */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.4 }}
          className="bg-white/90 backdrop-blur-md py-8 px-6 shadow-xl rounded-3xl border border-gray-100 sm:px-10"
        >
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Section: 1-Click Pre-seeded Test Scenarios */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-amber-500" />
                Select a Test Scenario (1-Click Login)
              </h2>
              <span className="text-xs text-gray-400">Pre-seeded Synthetic Data</span>
            </div>

            <div className="grid gap-3 sm:grid-cols-1">
              {DEMO_ACCOUNTS.map((account) => {
                const IconComponent = account.icon;
                const isSelected = email === account.email;

                return (
                  <button
                    key={account.email}
                    type="button"
                    onClick={() => {
                      setEmail(account.email);
                      handleLogin(account.email);
                    }}
                    disabled={isLoading}
                    className={`w-full text-left p-3.5 rounded-2xl border transition-all flex items-center justify-between group ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50/50 shadow-sm'
                        : 'border-gray-200 hover:border-blue-300 hover:bg-slate-50/70'
                    }`}
                  >
                    <div className="flex items-center gap-3.5">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-100 to-gray-200 flex items-center justify-center text-gray-700 group-hover:scale-105 transition-transform shadow-sm">
                        <IconComponent className="w-5 h-5 text-gray-700" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-gray-900">
                            {account.name}
                          </span>
                          <span
                            className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${account.tagColor}`}
                          >
                            {account.tag}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">{account.description}</p>
                      </div>
                    </div>
                    <div className="text-right pl-3 flex-shrink-0">
                      <span className="text-xs font-bold text-gray-700 block">{account.amount}</span>
                      <span className="text-[11px] text-gray-400">Score: {account.score}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-3 text-gray-400 font-medium">Or Sign In Manually</span>
            </div>
          </div>

          {/* Manual Login Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleLogin(email);
            }}
            className="space-y-4"
          >
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Applicant Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. rahul.sharma@email.com"
                  required
                  className="block w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Password <span className="text-gray-400 font-normal">(Default: password123)</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="block w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                />
              </div>
            </div>

            <div className="pt-2 flex flex-col sm:flex-row gap-3">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 py-2.5 px-4 rounded-xl text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? 'Verifying...' : 'Sign In as Selected Borrower'}
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                type="button"
                onClick={handleGuestLogin}
                disabled={isLoading}
                className="py-2.5 px-5 rounded-xl text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 border border-gray-200 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <User className="w-4 h-4 text-gray-600" />
                Continue as Guest
              </button>
            </div>
          </form>
        </motion.div>

        {/* Footer Note */}
        <p className="mt-6 text-center text-xs text-gray-500">
          Designed for Non-Banking Financial Company (NBFC) digital loan sales automation.
          <br />
          Demonstrates Master-Worker agentic collaboration and automated underwriting.
        </p>
      </div>
    </div>
  );
}
