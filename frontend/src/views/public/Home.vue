<script setup>
import { ref } from 'vue'

const hospitalStats = [
  { label: 'OPD Patients served today', value: '450+' },
  { label: 'Specialized Departments', value: '24' },
  { label: 'Excellence in Healthcare', value: '15 Yrs' },
]

const quickServices = [
  { title: 'Book Appointment', desc: 'Schedule a visit with your preferred doctor.', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z', link: '/book-appointment', color: 'primary' },
  { title: 'Lab Reports', desc: 'Securely access your test results online.', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10', link: '/login', color: 'secondary' },
  { title: 'Teleconsultation', desc: 'Consult our doctors from your home.', icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z', link: '/book-appointment', color: 'primary' },
]
</script>

<template>
  <div class="landing">
    <nav class="nav">
      <div class="logo">Ward<span>-</span>Wizard</div>
      
      <div class="nav-right">
        <button class="btn-ghost" @click="$router.push('/login')">Log in</button>
        <button class="btn-primary" @click="$router.push('/login?mode=signup')">Sign-up</button>
      </div>
    </nav>

    <section class="hero-bg">
      <div class="hero">
        <div class="hero-content">
          <div class="hero-badge">
            <div class="badge-dot"></div>
            <span class="badge-text">Trusted by hospitals & patients</span>
          </div>
          <h1 class="hero-headline">
            <span class="sans">Care that</span><br>
            <span class="serif" style="letter-spacing: 3px;">flows without</span><br>
            <span class="sans">friction.</span>
          </h1>
          <p class="hero-sub">Ward-Wizard unifies patient records, ward operations, and redundant workflows into one intelligent platform, so your teams can focus on healing, not paperwork.</p>
          <div class="hero-cta">
            <button class="cta-main" @click="$router.push('/login')">
              Launch Dashboard →
            </button>
            
          </div>
          <div class="hero-stats">
            <div class="stat-item">
              <span class="stat-num">Smart</span>
              <span class="stat-label">Faster admissions</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">3</span>
              <span class="stat-label">Core Dashboards</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">Live</span>
              <span class="stat-label">Dashboard Preview</span>
            </div>
          </div>
        </div>
        <div class="hero-visual">
          <div class="dash-card main-dash">
            <div class="dash-header">
              <div>
                <div class="dash-title">Hospital Overview</div>
                <div class="dash-meta">Last updated 2 mins ago</div>
              </div>
              <div style="width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 6px #22c55e55"></div>
            </div>
            <div class="vitals-grid">
              <div class="vital-card">
                <div class="vital-icon green">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                </div>
                <div class="vital-val">16</div>
                <div class="vital-lbl">Admitted Patients</div>
                <div class="vital-trend trend-up">↑ 4% today</div>
              </div>
              <div class="vital-card">
                <div class="vital-icon blue">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                </div>
                <div class="vital-val">26m</div>
                <div class="vital-lbl">OPD Voice-Recordings</div>
                <div class="vital-trend trend-down">↓ 8m this week</div>
              </div>
              <div class="vital-card">
                <div class="vital-icon amber">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                </div>
                <div class="vital-val">342</div>
                <div class="vital-lbl">Total Healed</div>
                <div class="vital-trend trend-up">↑ 9 new today</div>
              </div>
              <div class="vital-card">
                <div class="vital-icon rose">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#e11d48" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                </div>
                <div class="vital-val">97%</div>
                <div class="vital-lbl">Inventory</div>
                <div class="vital-trend trend-up">↑ 2%</div>
              </div>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
              <span style="font-size:12px;font-weight:500;color:var(--text-primary)">Today's patients</span>
              <span style="font-size:11px;color:var(--teal-mid);cursor:pointer">View all →</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px">
              <div class="patients-row">
                <div class="avatar av1">RK</div>
                <div class="avatar av2">MA</div>
                <div class="avatar av3">JP</div>
                <div class="avatar av4">SL</div>
                <div class="avatar av-more">+8</div>
              </div>
            </div>
            <div class="progress-bar-wrap" style="margin-top:16px">
              <div class="pb-row"><span>Ward capacity</span><span>84 / 100</span></div>
              <div class="pb-track"><div class="pb-fill" style="width:84%"></div></div>
            </div>
          </div>
          <div class="float-card fc1">
            <div class="fc-label">OPD Visits Today</div>
            <div class="fc-val">24</div>
            <div class="fc-sub" style="color:var(--teal-mid);font-weight:500;font-size:12px">↑ 6 more than avg</div>
            <div class="mini-bar-row">
              <div class="mini-bar" style="height:14px"></div>
              <div class="mini-bar" style="height:20px"></div>
              <div class="mini-bar active" style="height:28px"></div>
              <div class="mini-bar" style="height:18px"></div>
              <div class="mini-bar active" style="height:32px"></div>
              <div class="mini-bar" style="height:22px"></div>
              <div class="mini-bar active" style="height:32px"></div>
            </div>
          </div>
          <div class="float-card fc2">
            <div class="fc-label">Active</div>
            <div style="display:flex;align-items:center;gap:8px">
              <div style="width:10px;height:10px;border-radius:50%;background:#22c55e;box-shadow:0 0 6px #22c55e66"></div>
              <span style="font-size:15px;font-weight:600;color:#16a34a">AI Engine Online</span>
            </div>
            <div class="fc-sub">No critical alerts</div>
            <div class="pulse-row">
              <div class="pulse-dot active"></div>
              <div class="pulse-dot active"></div>
              <div class="pulse-dot active"></div>
              <div class="pulse-dot"></div>
              <div class="pulse-dot"></div>
              <span style="font-size:10px;color:var(--text-muted);margin-left:4px">system normal</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="features">
      <div class="features-inner">
        <div class="section-label">What we offer</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:flex-start;margin-bottom:48px">
          <h2 class="section-title"><span class="sans" style="font-family:'Inter',sans-serif;font-weight:600">Every ward,</span><br><span class="serif">every workflow</span></h2>
          <p class="section-sub" style="margin-bottom:0;padding-top:8px">Purpose-built modules that integrate seamlessly - Ward-Wizard keeps every touchpoint connected.</p>
        </div>
        <div class="feat-grid">
          <div class="feat-card">
            <div class="feat-icon-wrap">
              <svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
            </div>
            <div class="feat-title">Smart Patient Dashboard</div>
            <div class="feat-desc">Real-time overview of every admitted patient - vitals, prescriptions, and doctor notes in one unified view.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon-wrap">
              <svg viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            </div>
            <div class="feat-title">SOP Reviews</div>
            <div class="feat-desc">AI-assisted SOP lookups, to minimize document searching, and allowing staff to focus on what matters</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon-wrap">
              <svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </div>
            <div class="feat-title">Staff Scheduling</div>
            <div class="feat-desc">Automated shift management with conflict detection, leave tracking, and per-department allocation tools.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon-wrap">
              <svg viewBox="0 0 24 24"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
            </div>
            <div class="feat-title">Billing & Insurance</div>
            <div class="feat-desc">End-to-end revenue cycle management with automated claim submission, remittance reconciliation, and audit trails.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon-wrap">
              <svg viewBox="0 0 24 24"><rect x="1" y="4" width="22" height="16" rx="2"/><path d="M1 10h22"/></svg>
            </div>
            <div class="feat-title">Pharmacy Integration</div>
            <div class="feat-desc">Prescription routing, drug inventory alerts, and cross-ward medication tracking — all in real time.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon-wrap">
              <svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
            <div class="feat-title">Live consultation recording</div>
            <div class="feat-desc">Doctors record the consultation and get a structured summary, eliminating the need for updating records</div>
          </div>
        </div>
      </div>
    </section>

    <section class="social-proof">
      
      <div class="section-label">What teams are saying</div>
      <h2 class="section-title" style="margin-bottom:40px"><span style="font-family:'Inter',sans-serif;font-weight:600">Trusted by those who</span> <span class="serif">save lives</span></h2>
      <div class="testimonials">
        <div class="testi-card">
          <div class="testi-quote">"The admission flow went from 40 minutes to under <em>eight</em>. Our ER nurses call it the best upgrade in a decade."</div>
          <div class="testi-author">
            <div class="testi-av" style="background:#d4eddf;color:#166534">DR</div>
            <div><div class="testi-name">Dr. Reena Mehta</div><div class="testi-role">Chief of Emergency, Apollo Delhi</div></div>
          </div>
        </div>
        <div class="testi-card">
          <div class="testi-quote">"Billing reconciliation used to take our team three days per month. Ward-Wizard <em>automated</em> 90% of it."</div>
          <div class="testi-author">
            <div class="testi-av" style="background:#dbeafe;color:#1e40af">AK</div>
            <div><div class="testi-name">Arjun Khanna</div><div class="testi-role">CFO, Fortis Gurgaon</div></div>
          </div>
        </div>
        <div class="testi-card">
          <div class="testi-quote">"I can see the status of every ward from my phone. <em>Complete visibility</em> was something we never thought was possible."</div>
          <div class="testi-author">
            <div class="testi-av" style="background:#fef3c7;color:#92400e">SP</div>
            <div><div class="testi-name">Sunita Pillai</div><div class="testi-role">Hospital Director, Manipal Mysuru</div></div>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-section">
      <div class="cta-grid-bg"></div>
      <div class="cta-inner" style="position:relative;z-index:1">
        <div>
          <h2 class="cta-headline"><span style="font-family:'Inter',sans-serif;font-weight:600">Ready to transform</span><br><span class="serif">your hospital?</span></h2>
          <p class="cta-desc">Join the healthcare facilities that run smarter, safer operations with Ward-Wizard.</p>
          
        </div>
        
      </div>
    </section>

    <footer class="footer">
      <div class="footer-logo">Ward<span>-</span>Wizard</div>
      
      <div class="footer-copy">
        <div class="footer-copy">© 2026 Ward-Wizard. Team-13, CodeCrew</div>

      </div>
    </footer>
  </div>
</template>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600&display=swap');
  *{margin:0;padding:0;box-sizing:border-box}
  :root{
    --white:#ffffff;
    --off-white:#f8f7f5;
    --light-gray:#f0eeea;
    --border:#e8e4dd;
    --text-primary:#0f0e0d;
    --text-secondary:#6b6762;
    --text-muted:#9e9993;
    --accent:#1a4d3a;
    --accent-light:#2d7a5e;
    --accent-soft:#e8f4f0;
    --teal-mid:#3d9b7a;
    --gold:#b8955a;
    --gold-light:#f5efe3;
  }
  body{font-family:'Inter',sans-serif;background:var(--white);color:var(--text-primary);overflow-x:hidden}
  .serif{font-family:'Instrument Serif',Georgia,serif}
  .nav{display:flex;align-items:center;justify-content:space-between;padding:22px 60px;border-bottom:0px solid var(--border);background:rgba(255,255,255,0.95);backdrop-filter:blur(12px);position:sticky;top:0;z-index:100}
  .logo{font-family:'Inter',sans-serif;font-weight:600;font-size:18px;letter-spacing:-0.02em;color:var(--text-primary)}
  .logo span{color:var(--accent)}
  .nav-links{display:flex;align-items:center;gap:32px}
  .nav-links a{font-size:14px;color:var(--text-secondary);text-decoration:none;transition:color 0.2s}
  .nav-links a:hover{color:var(--text-primary)}
  .nav-right{display:flex;align-items:center;gap:12px}
  .btn-ghost{font-size:14px;font-weight:500;color:var(--text-primary);background:none;border:none;cursor:pointer;padding:8px 16px;border-radius:8px;transition:background 0.2s}
  .btn-ghost:hover{background:var(--light-gray)}
  .btn-primary{font-size:14px;font-weight:500;color:#fff;background:var(--accent);border:none;cursor:pointer;padding:9px 20px;border-radius:8px;transition:all 0.2s}
  .btn-primary:hover{background:var(--accent-light);transform:translateY(-1px)}
  .hero{padding:80px 60px 60px;display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center;max-width:1400px;margin:0 auto}
  .hero-badge{display:inline-flex;align-items:center;gap:8px;background:var(--accent-soft);border:1px solid #b8ddd2;border-radius:100px;padding:6px 14px;margin-bottom:28px}
  .badge-dot{width:7px;height:7px;border-radius:50%;background:var(--teal-mid)}
  .badge-text{font-size:12px;font-weight:500;color:var(--accent);letter-spacing:0.04em;text-transform:uppercase}
  .hero-headline{font-size:58px;line-height:1.06;letter-spacing:-0.03em;margin-bottom:24px}
  .hero-headline .serif{font-style:italic;color:var(--accent)}
  .hero-headline .sans{font-weight:600;font-family:'Inter',sans-serif}
  .hero-sub{font-size:17px;line-height:1.7;color:#252525;max-width:480px;margin-bottom:40px;font-weight:400}
  .hero-cta{display:flex;align-items:center;gap:16px}
  .cta-main{font-size:15px;font-weight:500;color:#fff;background:var(--accent);border:none;cursor:pointer;padding:14px 28px;border-radius:10px;transition:all 0.2s;display:flex;align-items:center;gap:8px}
  .cta-main:hover{background:var(--accent-light);transform:translateY(-2px);box-shadow:0 8px 24px rgba(26,77,58,0.25)}
  .cta-secondary{font-size:15px;font-weight:500;color:var(--text-primary);background:none;border:1.5px solid var(--border);cursor:pointer;padding:14px 28px;border-radius:10px;transition:all 0.2s}
  .cta-secondary:hover{border-color:var(--text-muted);background:var(--off-white)}
  .hero-stats{display:flex;gap:36px;margin-top:48px;padding-top:36px;border-top:1px solid var(--border)}
  .stat-item{display:flex;flex-direction:column;gap:4px}
  .stat-num{font-family:'Inter',sans-serif;font-size:28px;font-weight:600;letter-spacing:-0.03em;color:var(--text-primary)}
  .stat-num sup{font-size:14px;vertical-align:super}
  .stat-label{font-size:12px;color:#272727;letter-spacing:0.02em}
  .hero-visual{position:relative;height:520px}
  .dash-card{background:var(--white);border:1px solid var(--border);border-radius:20px;padding:24px;box-shadow:0 2px 20px rgba(0,0,0,0.06)}
  .main-dash{position:absolute;top:0;right:0;width:100%;max-width:440px;z-index:2}
  .dash-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
  .dash-title{font-size:13px;font-weight:600;color:var(--text-primary);letter-spacing:-0.01em}
  .dash-meta{font-size:11px;color:var(--text-muted)}
  .vitals-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px}
  .vital-card{background:var(--off-white);border-radius:12px;padding:14px}
  .vital-icon{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:8px}
  .vital-icon svg{width:14px;height:14px}
  .vital-icon.green{background:#d4eddf}
  .vital-icon.blue{background:#dbeafe}
  .vital-icon.amber{background:#fef3c7}
  .vital-icon.rose{background:#ffe4e6}
  .vital-val{font-size:20px;font-weight:600;letter-spacing:-0.03em;color:var(--text-primary)}
  .vital-lbl{font-size:11px;color:var(--text-muted);margin-top:2px}
  .vital-trend{display:inline-flex;align-items:center;gap:3px;font-size:10px;font-weight:500;margin-top:4px}
  .trend-up{color:#16a34a}
  .trend-down{color:#dc2626}
  .patients-row{display:flex;align-items:center;gap:-6px;margin-bottom:6px}
  .avatar{width:28px;height:28px;border-radius:50%;border:2px solid #fff;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:600;margin-right:-6px}
  .av1{background:#dbeafe;color:#1e40af}
  .av2{background:#d4eddf;color:#166534}
  .av3{background:#fef3c7;color:#92400e}
  .av4{background:#ffe4e6;color:#9f1239}
  .av-more{background:var(--light-gray);color:var(--text-muted)}
  .patients-label{font-size:12px;color:var(--text-secondary);margin-left:14px}
  .progress-bar-wrap{margin-top:12px}
  .pb-row{display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted);margin-bottom:6px}
  .pb-track{height:6px;background:var(--light-gray);border-radius:100px;overflow:hidden}
  .pb-fill{height:100%;border-radius:100px;background:linear-gradient(90deg,var(--teal-mid),var(--accent-light))}
  .float-card{position:absolute;background:var(--white);border:1px solid var(--border);border-radius:16px;padding:16px;box-shadow:0 4px 24px rgba(0,0,0,0.08)}
  .fc1{bottom:40px;left:-60px;width:190px;z-index:3}
  .fc2{top:180px;right:-20px;width:190px;z-index:3}
  .fc-label{font-size:10px;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-muted);margin-bottom:8px}
  .fc-val{font-size:22px;font-weight:600;letter-spacing:-0.03em;color:var(--text-primary)}
  .fc-sub{font-size:11px;color:var(--text-secondary);margin-top:2px}
  .mini-bar-row{display:flex;gap:4px;margin-top:10px;align-items:flex-end;height:32px}
  .mini-bar{width:12px;border-radius:3px;background:var(--accent-soft)}
  .mini-bar.active{background:var(--teal-mid)}
  .pulse-row{display:flex;gap:3px;margin-top:8px;align-items:center}
  .pulse-dot{width:6px;height:6px;border-radius:50%;background:var(--light-gray)}
  .pulse-dot.active{background:var(--teal-mid)}
  .features{padding:80px 60px;background:var(--off-white);border-top:1px solid var(--border)}
  .features-inner{max-width:1400px;margin:0 auto}
  .section-label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:var(--teal-mid);margin-bottom:16px}
  .section-title{font-size:42px;line-height:1.1;letter-spacing:-0.025em;margin-bottom:16px}
  .section-title .serif{color:var(--accent);font-style:italic}
  .section-sub{font-size:16px;color:var(--text-secondary);line-height:1.6;max-width:520px;margin-bottom:56px}
  .feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2px}
  .feat-card{background:var(--white);padding:36px 32px;transition:all 0.3s;cursor:default;position:relative;overflow:hidden}
  .feat-card:hover{background:var(--accent);transform:translateY(-2px);z-index:2;box-shadow:0 12px 40px rgba(26,77,58,0.2)}
  .feat-card:hover .feat-title,.feat-card:hover .feat-desc{color:#fff}
  .feat-card:hover .feat-icon-wrap{background:rgba(255,255,255,0.15)}
  .feat-card:hover .feat-icon-wrap svg{stroke:#fff}
  .feat-icon-wrap{width:44px;height:44px;border-radius:12px;background:var(--accent-soft);display:flex;align-items:center;justify-content:center;margin-bottom:20px;transition:background 0.3s}
  .feat-icon-wrap svg{width:20px;height:20px;stroke:var(--accent);fill:none;stroke-width:1.5;transition:stroke 0.3s}
  .feat-title{font-size:16px;font-weight:600;color:var(--text-primary);margin-bottom:10px;letter-spacing:-0.01em;transition:color 0.3s}
  .feat-desc{font-size:14px;color:var(--text-secondary);line-height:1.65;transition:color 0.3s}
  .social-proof{padding:80px 60px;max-width:1400px;margin:0 auto}
  .logos-row{display:flex;align-items:center;gap:48px;margin-bottom:60px;opacity:0.5}
  .logos-row .lname{font-size:13px;font-weight:600;letter-spacing:-0.01em;color:var(--text-secondary)}
  .testimonials{display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px}
  .testi-card{background:var(--off-white);border-radius:20px;padding:28px;border:1px solid var(--border)}
  .testi-quote{font-size:15px;line-height:1.7;color:var(--text-primary);margin-bottom:20px;font-weight:400}
  .testi-quote em{font-family:'Instrument Serif',serif;font-style:italic;font-size:17px;color:var(--accent)}
  .testi-author{display:flex;align-items:center;gap:12px}
  .testi-av{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600}
  .testi-name{font-size:13px;font-weight:600;color:var(--text-primary)}
  .testi-role{font-size:12px;color:var(--text-muted)}
  .cta-section{padding:80px 60px;background:var(--accent);overflow:hidden;position:relative}
  .cta-inner{max-width:1400px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:60px}
  .cta-grid-bg{position:absolute;inset:0;opacity:0.06;background-image:linear-gradient(rgba(255,255,255,.4) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.4) 1px,transparent 1px);background-size:40px 40px}
  .cta-headline{font-size:44px;line-height:1.1;letter-spacing:-0.025em;color:#fff;margin-bottom:16px}
  .cta-headline .serif{font-style:italic;opacity:0.8}
  .cta-desc{font-size:16px;color:rgba(255,255,255,0.65);line-height:1.6;margin-bottom:32px}
  .cta-btns{display:flex;gap:12px;flex-wrap:wrap}
  .btn-white{font-size:14px;font-weight:600;color:var(--accent);background:#fff;border:none;cursor:pointer;padding:13px 26px;border-radius:10px;transition:all 0.2s}
  .btn-white:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,0.2)}
  .btn-outline-white{font-size:14px;font-weight:500;color:#fff;background:transparent;border:1.5px solid rgba(255,255,255,0.35);cursor:pointer;padding:13px 26px;border-radius:10px;transition:all 0.2s}
  .btn-outline-white:hover{border-color:rgba(255,255,255,0.7);background:rgba(255,255,255,0.08)}
  .cta-checklist{display:flex;flex-direction:column;gap:14px}
  .check-item{display:flex;align-items:center;gap:14px}
  .check-box{width:22px;height:22px;border-radius:6px;background:rgba(255,255,255,0.12);display:flex;align-items:center;justify-content:center;flex-shrink:0}
  .check-box svg{width:12px;height:12px;stroke:#fff;fill:none;stroke-width:2.5}
  .check-text{font-size:14px;color:rgba(255,255,255,0.8)}
  .footer{padding:40px 60px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
  .footer-logo{font-family:'Inter',sans-serif;font-weight:600;font-size:15px;color:var(--text-primary)}
  .footer-logo span{color:var(--accent)}
  .footer-copy{font-size:12px;color:var(--text-muted)}
  .footer-links{display:flex;gap:24px}
  .footer-links a{font-size:12px;color:var(--text-muted);text-decoration:none}
  .footer-links a:hover{color:var(--text-secondary)}
  .arrow{display:inline-block;transition:transform 0.2s}
  .cta-main:hover .arrow{transform:translateX(3px)}
  @keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
  .hero-content>*{animation:fadeUp 0.6s ease both}
  .hero-content>*:nth-child(1){animation-delay:0.05s}
  .hero-content>*:nth-child(2){animation-delay:0.12s}
  .hero-content>*:nth-child(3){animation-delay:0.2s}
  .hero-content>*:nth-child(4){animation-delay:0.28s}
  .hero-content>*:nth-child(5){animation-delay:0.36s}
  .mini-sparkline{display:flex;gap:2px;align-items:flex-end;height:28px;margin-top:8px}
  .spark-bar{width:8px;border-radius:2px;background:var(--accent-soft)}
  .spark-bar.hi{background:var(--teal-mid)}
  .hero-bg {
  background-image: url("/src/assets/hills_6.jpg");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
 
  position: relative;
  
}
.hero-bg::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.62); /* adjust opacity here */
  z-index: 0;
}
.hero-bg > * {
  position: relative;
  z-index: 1;
}
</style>
