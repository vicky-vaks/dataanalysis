import { useState, useEffect, useRef, useMemo } from 'react'
import axios from 'axios'
import {
  TrendingUp, Target, BrainCircuit, Github,
  Cpu, Moon, Sun, Upload, Download, Search, CheckCircle2,
  ChevronRight, BarChart3, PieChart as PieIcon, LineChart as LineIcon,
  Filter, Users, Briefcase, IndianRupee, Star, X
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, PieChart, Pie, AreaChart, Area
} from 'recharts'
import './index.css'

// For split deployment: In Dev: localhost:5000. In Prod: Render URL (must be set in Vercel Env Vars)
// For split deployment: In Dev: localhost:5000 (via proxy). In Prod: Relative path or Full URL
console.log("VITE_API_BASE:", import.meta.env.VITE_API_BASE)
console.log("MODE:", import.meta.env.MODE)
const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const JOB_ROLES = [
  "Data Scientist", "ML Engineer", "Software Engineer", "Data Analyst",
  "Backend Developer", "Frontend Developer", "Full Stack Developer",
  "DevOps Engineer", "Cloud Architect", "AI Researcher", "Data Engineer",
  "Product Manager (Tech)", "UX Designer", "Cybersecurity Analyst",
  "Blockchain Developer", "Mobile App Developer", "Embedded Systems Engineer",
  "QA Automation Engineer", "NOC Engineer", "Solutions Architect",
  "Technical Support Engineer", "Database Administrator", "Systems Analyst",
  "Game Developer", "AR/VR Developer", "Big Data Engineer", "Scrum Master",
  "Site Reliability Engineer", "Computer Vision Engineer", "NLP Scientist"
]

const SKILL_CATEGORIES = {
  "Languages": ["Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust", "Swift", "Kotlin", "PHP", "Ruby", "R", "SQL", "HTML/CSS", "Shell Scripting"],
  "Data Science & AI": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Keras", "OpenCV", "Generative AI", "LLMs", "Data Visualization", "Tableau", "PowerBI"],
  "Web & Mobile": ["React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot", "ASP.NET", "Flutter", "React Native", "Android", "iOS", "GraphQL", "REST APIs", "Tailwind CSS"],
  "Cloud & DevOps": ["AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "Terraform", "Ansible", "CI/CD", "Linux", "Nginx", "Microservices", "Serverless"],
  "Tools & Platforms": ["Git", "Jira", "Confluence", "Slack", "Figma", "Adobe XD", "Unity", "Unreal Engine", "Blender", "Salesforce", "SAP"],
  "Soft Skills": ["Communication", "Leadership", "Teamwork", "Problem Solving", "Critical Thinking", "Time Management", "Project Management", "Agile", "Scrum", "Adaptability", "Creativity"]
}

const ALL_SKILLS = Object.values(SKILL_CATEGORIES).flat()

function App() {
  const [activeTab, setActiveTab] = useState('DataLab')
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark')

  return (
    <div className="app-container">
      <nav className="sidebar">
        <div style={{ padding: '0 0.5rem', marginBottom: '2.5rem' }}>
          <h2 className="gradient-text" style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Cpu size={32} strokeWidth={2.5} /> HR Inteligencia
          </h2>
        </div>

        {[
          { id: 'DataLab', icon: BarChart3, label: 'Data Lab' },
          { id: 'Salary', icon: TrendingUp, label: 'Salary Predictor' },
          { id: 'Skills', icon: Target, label: 'Skill Optimizer' },
          { id: 'Recruiter', icon: BrainCircuit, label: 'Recruiter Portal' }
        ].map(item => (
          <div
            key={item.id}
            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => setActiveTab(item.id)}
          >
            <item.icon size={20} /> {item.label}
          </div>
        ))}

        <div style={{ marginTop: 'auto', padding: '1rem' }}>
          <button
            onClick={toggleTheme}
            style={{
              width: '100%', padding: '0.75rem', borderRadius: '12px', background: 'var(--bg-primary)',
              border: '1px solid var(--glass-border)', color: 'var(--text-primary)', cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px'
            }}
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            {theme === 'dark' ? 'Light Mode' : 'Night Mode'}
          </button>
          <div style={{ marginTop: '1rem', fontSize: '0.7rem', color: 'var(--text-dim)', textAlign: 'center', wordBreak: 'break-all' }}>
            API: {API_BASE}
          </div>
        </div>
      </nav>

      <main className="main-content">
        <header style={{ marginBottom: '3rem' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800 }}>
            {activeTab === 'DataLab' ? "AI HR Analytics Hub" :
              activeTab === 'Salary' ? "Salary Intelligence" :
                activeTab === 'Skills' ? "Skill Roadmap" : "Candidate Discovery"}
          </h1>
          <p style={{ color: 'var(--text-dim)' }}>Manage and analyze your talent ecosystem.</p>
        </header>

        <section className="fade-in">
          {activeTab === 'DataLab' && <DataLab />}
          {activeTab === 'Salary' && <SalaryPredictor />}
          {activeTab === 'Skills' && <SkillOptimizer />}
          {activeTab === 'Recruiter' && <RecruiterPortal />}
        </section>
      </main>
    </div>
  )
}

function DataLab() {
  const [file, setFile] = useState(null)
  const [marketData, setMarketData] = useState(null)
  const [candidates, setCandidates] = useState([])
  const [isLoaded, setIsLoaded] = useState(false)
  const [status, setStatus] = useState('')
  const fileInputRef = useRef(null)

  // Mapping States
  const [mappingRequired, setMappingRequired] = useState(false)
  const [availableColumns, setAvailableColumns] = useState([])
  const [columnMapping, setColumnMapping] = useState({
    role: '',
    salary: '',
    skills: '',
    experience: ''
  })

  // Filter States
  const [filters, setFilters] = useState({
    role: 'All',
    experience: 5,
    selectedSkills: []
  })

  const handleUpload = async (mapping = null) => {
    if (!file) return
    setStatus(mapping ? 're-analyzing...' : 'analyzing...')

    // If not mapping, clear states
    if (!mapping) {
      setMarketData(null)
      setCandidates([])
      setIsLoaded(false)
      setMappingRequired(false)
    }

    const formData = new FormData()
    formData.append('file', file)

    try {
      // 1. Upload the file first
      await axios.post(`${API_BASE}/upload_csv`, formData)

      // 2. Try to get analysis (optionally with mapping)
      const res = await axios.post(`${API_BASE}/market_data`, { mapping })
      const data = res.data

      if (data.error === 'mapping_required') {
        setMappingRequired(true)
        setAvailableColumns(data.columns)
        setColumnMapping(data.detected || {})
        setStatus('mapping_needed')
        return
      }

      // 3. Success! Set stats and load candidates
      setMarketData(data)
      setMappingRequired(false)

      const candRes = await axios.post(`${API_BASE}/match_candidates`, {
        skills_required: filters.selectedSkills.length > 0 ? filters.selectedSkills : ["Python", "SQL"],
        top_n: 10
      })
      setCandidates(candRes.data.candidates)

      setIsLoaded(true)
      setStatus('success')
    } catch (err) {
      console.error("Analysis Failure:", err)
      let errorMsg = "Connection failure or incompatible CSV."
      if (err.response?.data?.error) {
        errorMsg = typeof err.response.data.error === 'object'
          ? JSON.stringify(err.response.data.error)
          : err.response.data.error
      }
      setStatus(`error: ${errorMsg}`)
    }
  }

  const updateCandidates = async () => {
    try {
      const res = await axios.post(`${API_BASE}/match_candidates`, {
        skills_required: filters.selectedSkills.length > 0 ? filters.selectedSkills : ["Python", "SQL"],
        top_n: 10
      })
      setCandidates(res.data.candidates)
    } catch (err) { console.error(err) }
  }

  useEffect(() => {
    if (isLoaded) updateCandidates()
  }, [filters.selectedSkills])

  // Filtering Logic for Charts
  const filteredExpData = useMemo(() => {
    if (!marketData) return []
    return marketData.exp_salary
  }, [marketData])

  if (!isLoaded) {
    return (
      <div className="glass-card" style={{ maxWidth: mappingRequired ? '900px' : '600px', margin: '0 auto', textAlign: 'center', padding: '4rem 2rem' }}>
        {!mappingRequired ? (
          <>
            <div onClick={() => fileInputRef.current.click()} style={{ border: '2px dashed var(--glass-border)', padding: '4rem', borderRadius: '24px', cursor: 'pointer' }}>
              <Upload size={48} color="var(--primary)" style={{ marginBottom: '1.5rem' }} />
              <h2>Universal CSV Importer</h2>
              <p style={{ color: 'var(--text-dim)', marginTop: '0.5rem' }}>Upload any recruitment sheet to begin AI analysis</p>
              <input type="file" hidden ref={fileInputRef} onChange={(e) => setFile(e.target.files[0])} accept=".csv" />
            </div>
            {file && (
              <button onClick={() => handleUpload()} className="btn-primary" style={{ marginTop: '2rem', width: '220px' }}>
                {status === 'analyzing...' ? 'Sifting Data...' : 'Analyze CSV Structure'}
              </button>
            )}
          </>
        ) : (
          <div className="fade-in">
            <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
              <Briefcase color="var(--primary)" /> Finalize Column Mapping
            </h2>
            <p style={{ color: 'var(--text-dim)', marginBottom: '2rem' }}>We couldn't perfectly identify your column headers. Please map them below:</p>

            <div className="grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)', textAlign: 'left', gap: '1.5rem', marginBottom: '2.5rem' }}>
              {[
                { label: 'Job Role / Title (Required)', key: 'role' },
                { label: 'Skills / Tools (Recommended)', key: 'skills' },
                { label: 'Years of Experience (Optional)', key: 'experience' }
              ].map(field => (
                <div key={field.key}>
                  <label style={{ fontSize: '0.85rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.5rem' }}>{field.label}</label>
                  <select
                    value={columnMapping[field.key] || ''}
                    onChange={(e) => setColumnMapping({ ...columnMapping, [field.key]: e.target.value })}
                    style={{ width: '100%', padding: '0.8rem', borderRadius: '12px', background: 'var(--bg-primary)', border: '1px solid var(--glass-border)', color: 'var(--text-primary)' }}
                  >
                    <option value="">Select Column Header...</option>
                    {availableColumns.map(col => <option key={col} value={col}>{col}</option>)}
                  </select>
                </div>
              ))}
            </div>

            <button
              onClick={() => handleUpload(columnMapping)}
              className="btn-primary"
              style={{ width: '100%', padding: '1.25rem' }}
              disabled={!columnMapping.role}
            >
              Confirm and Generate High-Fidelity Insights
            </button>
            <p
              onClick={() => { setMappingRequired(false); setFile(null); setStatus('') }}
              style={{ marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-dim)', cursor: 'pointer', textDecoration: 'underline' }}
            >
              Cancel and try another file
            </p>
          </div>
        )}

        {status.startsWith('error') && (
          <div style={{ marginTop: '1.5rem', color: '#ef4444', background: '#fee2e2', padding: '1rem', borderRadius: '12px', border: '1px solid #fecaca' }}>
            <strong>Analysis Failed:</strong> {status.split(': ')[1]}
            <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>Please verify your CSV file structure and try again.</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '2.5rem' }}>
      {/* Left Side: Graphs and Candidates */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <div className="grid" style={{ marginTop: 0 }}>
          <div className="glass-card">
            <h3 style={{ marginBottom: '1.5rem' }}>Demand Mix</h3>
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={marketData?.skill_demand.slice(0, 5) || []}>
                  <XAxis dataKey="skill" tick={{ fill: 'var(--text-dim)', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis hide />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--primary)" radius={[6, 6, 0, 0]} barSize={30} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Star size={24} color="#f59e0b" fill="#f59e0b" /> Top 10 Ideal Candidates
            </h3>
            <span className="glass" style={{ fontSize: '0.8rem', padding: '6px 12px', borderRadius: '20px' }}>AI Match Enabled</span>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-dim)', textAlign: 'left' }}>
                <th style={{ padding: '1rem' }}>Expert Name</th>
                <th style={{ padding: '1rem' }}>Experience</th>
                <th style={{ padding: '1rem' }}>Fit Score</th>
              </tr>
            </thead>
            <tbody>
              {candidates.slice(0, 10).map((cand, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                  <td style={{ padding: '1rem' }}>
                    <div style={{ fontWeight: 700 }}>{cand.Name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{cand.Email}</div>
                  </td>
                  <td style={{ padding: '1rem' }}>{cand['Experience Level']}</td>
                  <td style={{ padding: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ flex: 1, height: '6px', background: 'var(--bg-primary)', borderRadius: '10px' }}>
                        <div style={{ width: `${cand.score}%`, height: '100%', background: 'linear-gradient(to right, var(--primary), var(--secondary))', borderRadius: '10px' }} />
                      </div>
                      <span style={{ fontWeight: 800, color: 'var(--primary)', minWidth: '40px' }}>{cand.score}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Right Side: Filters */}
      <aside style={{ position: 'sticky', top: '2rem', height: 'fit-content' }}>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '2rem' }}>
            <Filter size={20} /> HR Filters
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '0.75rem' }}>Job Roll</label>
              <select
                value={filters.role}
                onChange={(e) => setFilters({ ...filters, role: e.target.value })}
                style={{ width: '100%', padding: '0.8rem', borderRadius: '12px', background: 'var(--bg-primary)', border: '1px solid var(--glass-border)', color: 'var(--text-primary)' }}
              >
                <option value="All">All Categories</option>
                {(marketData?.filters?.roles || JOB_ROLES).map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '0.75rem' }}>Experience Level ({filters.experience}y+)</label>
              {(marketData?.filters?.experience && marketData.filters.experience.length > 0) ? (
                <select
                  value={filters.experience}
                  onChange={(e) => setFilters({ ...filters, experience: parseInt(e.target.value) })}
                  style={{ width: '100%', padding: '0.8rem', borderRadius: '12px', background: 'var(--bg-primary)', border: '1px solid var(--glass-border)', color: 'var(--text-primary)' }}
                >
                  {marketData.filters.experience.map(y => <option key={y} value={y}>{y} Years</option>)}
                </select>
              ) : (
                <input
                  type="range" min="0" max="25"
                  value={filters.experience}
                  onChange={(e) => setFilters({ ...filters, experience: parseInt(e.target.value) })}
                  style={{ width: '100%' }}
                />
              )}
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '0.75rem' }}>Required Skills</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(marketData?.filters?.skills || ALL_SKILLS).map(skill => (
                  <div
                    key={skill}
                    onClick={() => {
                      const newSkills = filters.selectedSkills.includes(skill)
                        ? filters.selectedSkills.filter(s => s !== skill)
                        : [...filters.selectedSkills, skill]
                      setFilters({ ...filters, selectedSkills: newSkills })
                    }}
                    style={{
                      padding: '6px 12px', borderRadius: '30px', cursor: 'pointer', fontSize: '0.75rem',
                      background: filters.selectedSkills.includes(skill) ? 'var(--primary)' : 'var(--bg-primary)',
                      color: filters.selectedSkills.includes(skill) ? 'white' : 'var(--text-secondary)',
                      border: '1px solid var(--glass-border)',
                      transition: 'all 0.2s'
                    }}
                  >
                    {skill}
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={() => setFilters({ role: 'All', experience: 5, selectedSkills: [] })}
              style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600, alignSelf: 'flex-start' }}
            >
              Reset Parameters
            </button>
          </div>
        </div>

        <div className="glass-card" style={{ marginTop: '1.5rem', padding: '1.25rem', background: 'var(--primary-glow)' }}>
          <p style={{ color: 'var(--primary)', fontSize: '0.8rem', fontWeight: 600 }}>Pro Tip:</p>
          <p style={{ fontSize: '0.8rem', marginTop: '4px' }}>AI Match weights "Experience" and "Specific Skills" 40% higher than general roles.</p>
        </div>
      </aside>
    </div>
  )
}

function SalaryPredictor() {
  const [form, setForm] = useState({ role: 'Data Scientist', location: 'Remote', experience_years: 5, skills: [] })
  const [prediction, setPrediction] = useState(null)

  const locations = ["Remote", "Bangalore, India", "San Francisco, CA", "Austin, TX", "London, UK", "Berlin, Germany", "Singapore", "New York, NY", "Sydney, Australia", "Toronto, Canada"]

  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setPrediction(null)
    try {
      const res = await axios.post(`${API_BASE}/predict_salary`, form)
      setPrediction(res.data.predicted_salary)
    } catch (err) {
      console.error(err);
      setError(err.message + (err.response ? ": " + JSON.stringify(err.response.data) : ""))
    }
  }

  return (
    <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
      <div className="glass-card">
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 600 }}>Target Role</label>
            <select
              value={form.role}
              onChange={e => setForm({ ...form, role: e.target.value })}
              style={{ width: '100%', padding: '1rem', borderRadius: '12px', background: 'var(--bg-primary)', border: '1px solid var(--glass-border)', color: 'var(--text-primary)' }}
            >
              {JOB_ROLES.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 600 }}>Base Location</label>
            <select
              value={form.location}
              onChange={e => setForm({ ...form, location: e.target.value })}
              style={{ width: '100%', padding: '1rem', borderRadius: '12px', background: 'var(--bg-primary)', border: '1px solid var(--glass-border)', color: 'var(--text-primary)' }}
            >
              {locations.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 600 }}>Years of Experience ({form.experience_years})</label>
            <input
              type="range" min="0" max="30" step="1"
              value={form.experience_years}
              onChange={e => setForm({ ...form, experience_years: e.target.value })}
              style={{ width: '100%' }}
            />
          </div>
          <button type="submit" className="btn-primary" style={{ padding: '1.25rem' }}>Calculate Global Average</button>
        </form>
      </div>

      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
        {error ? (
          <div style={{ color: 'red', textAlign: 'center' }}>
            <h3>Error</h3>
            <p>{error}</p>
            <p style={{ fontSize: '0.8rem' }}>Check your connection or Try again later.</p>
          </div>
        ) : prediction ? (
          <div className="fade-in" style={{ textAlign: 'center' }}>
            <h4 style={{ color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '2px', fontSize: '0.875rem' }}>Market Valuation</h4>
            <div className="gradient-text" style={{ fontSize: '5rem', margin: '1rem 0' }}>
              ₹{prediction} <span style={{ fontSize: '1.5rem', color: 'var(--text-dim)' }}>LPA</span>
            </div>
            <p style={{ color: 'var(--text-secondary)' }}>Based on aggregated industry standards for <b>2024-2025</b></p>
          </div>
        ) : (
          <div style={{ textAlign: 'center' }}>
            <TrendingUp size={64} color="var(--glass-border)" style={{ marginBottom: '2rem' }} />
            <h3 style={{ color: 'var(--text-dim)' }}>Enter details to initialize prediction</h3>
          </div>
        )}
      </div>
    </div>
  )
}

function SkillOptimizer() {
  const [targetRole, setTargetRole] = useState('Data Scientist')
  const [currentSkills, setCurrentSkills] = useState([])
  const [results, setResults] = useState(null)

  const [error, setError] = useState(null)

  const analyze = async () => {
    setError(null)
    try {
      const res = await axios.post(`${API_BASE}/recommend_skills`, {
        target_role: targetRole,
        current_skills: currentSkills
      })
      setResults(res.data)
    } catch (err) {
      console.error(err)
      setError(err.message + (err.response ? ": " + JSON.stringify(err.response.data) : ""))
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="glass-card">
        <h3 style={{ marginBottom: '2rem' }}>Select Desired Goal</h3>
        <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '300px' }}>
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 600 }}>Target Position</label>
            <select
              value={targetRole}
              onChange={e => {
                setTargetRole(e.target.value)
                setResults(null) // Reset results on role change
                setCurrentSkills([]) // Optional: clear selected skills
              }}
              style={{ width: '100%', padding: '1rem', borderRadius: '12px', background: 'var(--bg-primary)', border: '1px solid var(--glass-border)', color: 'var(--text-primary)' }}
            >
              {JOB_ROLES.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div style={{ flex: 2 }}>
            <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: 600 }}>Your Skill Inventory (Select what you know)</label>
            <div style={{ maxHeight: '400px', overflowY: 'auto', paddingRight: '10px' }}>
              {Object.entries(SKILL_CATEGORIES).map(([category, skills]) => (
                <div key={category} style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ fontSize: '0.9rem', color: 'var(--accent)', marginBottom: '0.8rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '4px' }}>{category}</h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {skills.map(skill => (
                      <div
                        key={skill}
                        onClick={() => currentSkills.includes(skill) ? setCurrentSkills(currentSkills.filter(s => s !== skill)) : setCurrentSkills([...currentSkills, skill])}
                        style={{
                          padding: '6px 14px', borderRadius: '40px', cursor: 'pointer', fontSize: '0.8rem',
                          background: currentSkills.includes(skill) ? 'var(--primary)' : 'var(--bg-primary)',
                          color: currentSkills.includes(skill) ? 'white' : 'var(--text-secondary)',
                          border: '1px solid var(--glass-border)',
                          transition: 'all 0.2s'
                        }}
                      >
                        {skill}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        <button onClick={analyze} className="btn-primary" style={{ marginTop: '2.5rem' }}>Map My Career Path</button>
        {error && <p style={{ color: 'red', marginTop: '1rem' }}>Error: {error}</p>}
      </div>

      {results && (
        <div className="grid">
          <div className="glass-card" style={{ borderLeft: '4px solid var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
            <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '1px', fontSize: '0.8rem' }}>Role Fit Score</h3>
            <div style={{ position: 'relative', width: '150px', height: '150px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[{ value: results.match_percentage }, { value: 100 - results.match_percentage }]}
                    cx="50%" cy="50%" innerRadius={55} outerRadius={70}
                    startAngle={90} endAngle={-270}
                    dataKey="value" stroke="none"
                  >
                    <Cell fill={results.match_percentage > 70 ? 'var(--secondary)' : 'var(--primary)'} />
                    <Cell fill="var(--glass-border)" />
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
                <span style={{ fontSize: '2rem', fontWeight: 800, color: 'white' }}>{results.match_percentage}%</span>
              </div>
            </div>
            <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>Match for {targetRole}</p>
          </div>

          <div className="glass-card" style={{ gridColumn: 'span 2' }}>
            <h3 style={{ marginBottom: '1.5rem' }}>Skills Gap Analysis</h3>
            <div style={{ display: 'flex', gap: '2rem' }}>
              <div style={{ flex: 1 }}>
                <h4 style={{ marginBottom: '1rem', color: 'var(--secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle2 size={18} /> You Have
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {results.matched_skills.length > 0 ? results.matched_skills.map(s => (
                    <div key={s} style={{ padding: '6px 12px', borderRadius: '8px', background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', border: '1px solid rgba(34, 197, 94, 0.2)', fontSize: '0.85rem' }}>{s}</div>
                  )) : <span style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>No matching skills yet</span>}
                </div>
              </div>
              <div style={{ width: '1px', background: 'var(--glass-border)' }}></div>
              <div style={{ flex: 1 }}>
                <h4 style={{ marginBottom: '1rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Target size={18} /> Required for Role
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {results.missing_skills.map(s => (
                    <div key={s} style={{ padding: '6px 12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-secondary)', border: '1px solid var(--glass-border)', fontSize: '0.85rem' }}>{s}</div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function RecruiterPortal() {
  const [reqSkills, setReqSkills] = useState([])
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(false)

  const [error, setError] = useState(null)

  const find = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await axios.post(`${API_BASE}/match_candidates`, {
        skills_required: reqSkills,
        top_n: 10
      })
      setCandidates(res.data.candidates)
    } catch (err) {
      console.error(err)
      setError(err.message + (err.response ? ": " + JSON.stringify(err.response.data) : ""))
    }
    setLoading(false)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="glass-card">
        <h3 style={{ marginBottom: '2rem' }}>Candidate Filter Parameters</h3>
        <label style={{ display: 'block', marginBottom: '1rem', fontWeight: 600 }}>Skillset Requirements</label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '2rem' }}>
          {ALL_SKILLS.map(skill => (
            <div
              key={skill}
              onClick={() => reqSkills.includes(skill) ? setReqSkills(reqSkills.filter(s => s !== skill)) : setReqSkills([...reqSkills, skill])}
              style={{
                padding: '10px 20px', borderRadius: '40px', cursor: 'pointer',
                background: reqSkills.includes(skill) ? 'var(--secondary)' : 'var(--bg-primary)',
                color: reqSkills.includes(skill) ? 'white' : 'var(--text-secondary)',
                border: '1px solid var(--glass-border)'
              }}
            >
              {skill}
            </div>
          ))}
        </div>
        <button onClick={find} className="btn-primary" style={{ minWidth: '240px' }}>
          {loading ? 'Sifting Talent Pool...' : 'Execute AI Search'}
        </button>
        {error && <p style={{ color: 'red', marginTop: '1rem' }}>Error: {error}</p>}
      </div>

      {candidates.length > 0 && (
        <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'var(--bg-primary)', borderBottom: '1px solid var(--glass-border)' }}>
                <th style={{ padding: '1.5rem' }}>Name & Identity</th>
                <th style={{ padding: '1.5rem' }}>Experience</th>
                <th style={{ padding: '1.5rem' }}>Match Probability</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((cand, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--glass-border)' }} className="fade-in">
                  <td style={{ padding: '1.5rem' }}>
                    <div style={{ fontWeight: 700 }}>{cand.Name}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{cand.Email}</div>
                  </td>
                  <td style={{ padding: '1.5rem' }}>{cand['Experience Level']}</td>
                  <td style={{ padding: '1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                      <div style={{ flex: 1, height: '6px', background: 'var(--bg-primary)', borderRadius: '10px' }}>
                        <div style={{ width: `${cand.score}%`, height: '100%', background: 'linear-gradient(to right, var(--primary), var(--secondary))', borderRadius: '10px' }} />
                      </div>
                      <span style={{ fontWeight: 800, color: 'var(--primary)' }}>{cand.score}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default App
