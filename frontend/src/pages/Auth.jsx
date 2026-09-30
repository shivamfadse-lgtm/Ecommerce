import React, { useState } from 'react';
import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, Truck, UserRound } from 'lucide-react';
import { api } from '../services/api';

const panelCopy = {
  login: { title: 'Welcome back', subtitle: 'Sign in to your Nanded delivery intelligence workspace.' },
  signup: { title: 'Create your account', subtitle: 'Create a secure SmartDeliver AI account to access the platform.' },
  forgot: { title: 'Reset your password', subtitle: 'Enter your email and we will send reset instructions if an account exists.' }
};

export default function Auth({ initialView = 'login', onAuthenticated }) {
  const [view, setView] = useState(initialView);
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm_password: '' });
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const copy = panelCopy[view];

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });
  const switchView = (next) => { setView(next); setError(''); setNotice(''); setShowPassword(false); };

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    setNotice('');
    setBusy(true);
    try {
      if (view === 'signup') {
        await api.register(form);
        setForm({ full_name: '', email: form.email, password: '', confirm_password: '' });
        switchView('login');
        setNotice('Account created successfully. Log in with your email and password.');
      } else if (view === 'forgot') {
        const response = await api.forgotPassword(form.email);
        setNotice(response.message);
      } else {
        const response = await api.login(form.email, form.password);
        onAuthenticated(response);
      }
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to complete this request.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f4f0e7] text-slate-900 flex items-center justify-center p-6">
      <div className="w-full max-w-5xl grid lg:grid-cols-[1.05fr_.95fr] bg-white shadow-2xl shadow-slate-900/10 border border-slate-200 overflow-hidden">
        <section className="hidden lg:flex bg-[#173b32] text-white p-12 flex-col justify-between min-h-[650px]">
          <div>
            <div className="flex items-center gap-3 mb-16"><div className="bg-[#d8e86a] text-[#173b32] p-3 font-black tracking-tight">SD</div><div className="text-xl font-bold">SmartDeliver <span className="text-[#d8e86a]">AI</span></div></div>
            <p className="text-xs uppercase tracking-[.2em] text-emerald-200/70 mb-4">Nanded, Maharashtra</p>
            <h2 className="text-4xl font-semibold leading-tight">Delivery intelligence for better local decisions.</h2>
            <p className="mt-6 text-emerald-100/75 leading-relaxed max-w-md">Securely access demand clusters, real road coverage, recommendations, and business impact analysis.</p>
          </div>
          <div className="flex items-center gap-3 text-sm text-emerald-100/70"><ShieldCheck className="w-5 h-5 text-[#d8e86a]" /> Protected workspace with role-based access</div>
        </section>
        <section className="p-7 sm:p-12 flex items-center">
          <div className="w-full max-w-md mx-auto">
            <div className="flex lg:hidden items-center gap-3 mb-10"><div className="bg-[#173b32] text-[#d8e86a] p-2.5 font-black">SD</div><div className="text-xl font-bold text-[#173b32]">SmartDeliver <span className="text-emerald-700">AI</span></div></div>
            <div className="mb-8"><p className="text-xs font-bold tracking-[.18em] text-emerald-700 uppercase">SmartDeliver AI</p><h1 className="text-3xl font-bold text-slate-900 mt-3">{copy.title}</h1><p className="text-sm text-slate-500 mt-2">{copy.subtitle}</p></div>
            <form onSubmit={submit} className="space-y-4">
              {view === 'signup' && <label className="block text-sm font-semibold text-slate-700">Full Name<div className="relative mt-2"><UserRound className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" /><input name="full_name" value={form.full_name} onChange={update} required className="w-full border border-slate-200 px-10 py-3.5 outline-none focus:border-emerald-700" placeholder="Enter your full name" /></div></label>}
              <label className="block text-sm font-semibold text-slate-700">Email Address<div className="relative mt-2"><Mail className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" /><input name="email" type="email" value={form.email} onChange={update} required className="w-full border border-slate-200 px-10 py-3.5 outline-none focus:border-emerald-700" placeholder="Enter your email" /></div></label>
              {view !== 'forgot' && <label className="block text-sm font-semibold text-slate-700">Password<div className="relative mt-2"><LockKeyhole className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" /><input name="password" type={showPassword ? 'text' : 'password'} value={form.password} onChange={update} required minLength={8} className="w-full border border-slate-200 px-10 pr-12 py-3.5 outline-none focus:border-emerald-700" placeholder="Enter your password" /><button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-3.5 text-slate-400" aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}</button></div></label>}
              {view === 'signup' && <label className="block text-sm font-semibold text-slate-700">Confirm Password<input name="confirm_password" type={showPassword ? 'text' : 'password'} value={form.confirm_password} onChange={update} required minLength={8} className="w-full border border-slate-200 px-4 py-3.5 mt-2 outline-none focus:border-emerald-700" placeholder="Confirm your password" /></label>}
              {error && <div className="border-l-4 border-red-500 bg-red-50 text-red-700 px-3 py-3 text-sm">{error}</div>}
              {notice && <div className="border-l-4 border-emerald-600 bg-emerald-50 text-emerald-800 px-3 py-3 text-sm">{notice}</div>}
              <button disabled={busy} className="w-full bg-[#173b32] hover:bg-emerald-900 disabled:opacity-60 text-white py-3.5 font-bold flex items-center justify-center gap-2">{busy ? 'Please wait...' : view === 'login' ? 'Login' : view === 'signup' ? 'Create Account' : 'Send Reset Instructions'}<ArrowRight className="w-4 h-4" /></button>
            </form>
            <div className="flex justify-between items-center mt-6 text-sm"><button onClick={() => switchView(view === 'forgot' ? 'login' : 'forgot')} className="text-emerald-800 font-semibold">{view === 'forgot' ? 'Back to Login' : 'Forgot Password?'}</button>{view !== 'forgot' && <button onClick={() => switchView(view === 'login' ? 'signup' : 'login')} className="text-emerald-800 font-semibold">{view === 'login' ? 'Create Account / Sign Up' : 'Already have an account? Login'}</button>}</div>
          </div>
        </section>
      </div>
    </div>
  );
}
