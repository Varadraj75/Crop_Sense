;(() => {
	let priceChartInstance = null
	let yieldChartInstance = null

	function showPage(pageId) {
		document.querySelectorAll('.page').forEach((p) => p.classList.add('hidden'))
		document.getElementById(`page-${pageId}`).classList.remove('hidden')
	}

	function initNav() {
		function handleNav(target) {
			if (!target) return
			const page = target.getAttribute('data-nav')
			if (page) {
				showPage(page)
				document.getElementById('mobile-nav').classList.add('hidden')
			}
		}
		document.querySelectorAll('.nav-btn').forEach((btn) => btn.addEventListener('click', (e) => handleNav(e.currentTarget)))
		document.querySelector('.start-btn')?.addEventListener('click', (e) => handleNav(e.currentTarget))
		document.getElementById('mobile-menu').addEventListener('click', () => {
			document.getElementById('mobile-nav').classList.toggle('hidden')
		})
	}

	function randomInt(min, max) {
		return Math.floor(Math.random() * (max - min + 1)) + min
	}

	// Crop Suggestion
	function initSuggestions() {
		document.getElementById('generate-suggestions').addEventListener('click', async () => {
			const results = document.getElementById('suggestion-results')
			const button = document.getElementById('generate-suggestions')
			
			// Get form values
			const soilType = document.getElementById('soil-type').value
			const location = document.getElementById('location').value
			const water = document.getElementById('water').value
			const pastCrops = document.getElementById('past-crops').value
			
			// Validate inputs
			if (!soilType || !location || !water || !pastCrops) {
				alert('Please fill in all fields before generating suggestions.')
				return
			}
			
			// Show loading state
			button.disabled = true
			button.textContent = 'Generating...'
			results.innerHTML = '<div class="animate-pulse text-slate-400">Getting crop suggestions...</div>'
			
			try {
				const response = await fetch('http://127.0.0.1:5000/get_suggestions', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						soil_type: soilType,
						location: location,
						water: water,
						past_crops: pastCrops
					})
				})
				
				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`)
				}
				
				const data = await response.json()
				results.innerHTML = ''
				
				// Display crop suggestions from API
				data.recommendations.forEach((crop) => {
					const emoji = getCropEmoji(crop.name)
					const card = document.createElement('div')
					card.className = 'rounded-md border border-slate-800 bg-slate-950 p-3'
					card.innerHTML = `
						<div class="text-lg font-semibold">${emoji} ${crop.name}</div>
						<div class="text-sm text-slate-300">Yield: ${crop.yield}</div>
						<div class="text-sm text-slate-300">Profit: ${crop.profit}</div>
						<div class="text-sm text-slate-300">Sustainability: ${crop.sustainability}</div>
					`
					results.appendChild(card)
				})
				
			} catch (error) {
				console.error('Error fetching crop suggestions:', error)
				results.innerHTML = '<div class="text-red-400">Error fetching suggestions. Please try again.</div>'
			} finally {
				// Reset button state
				button.disabled = false
				button.textContent = 'Generate Suggestions'
			}
		})
	}
	
	// Helper function to get crop emoji
	function getCropEmoji(cropName) {
		const emojiMap = {
			'Wheat': '🌾',
			'Rice': '🍚', 
			'Maize': '🌽',
			'Sugarcane': '🧃',
			'Cotton': '🧵',
			'Pulses': '🫘',
			'Paddy': '🍚',
			'Jute': '🌿',
			'Potato': '🥔'
		}
		return emojiMap[cropName] || '🌱'
	}

	// Weather & Soil (mock)
	function initWeatherSoil() {
		const forecast = document.getElementById('weather-forecast')
		const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
		const icons = ['☀️', '🌤️', '⛅', '🌧️', '⛈️', '🌫️']
		const today = new Date()
		forecast.innerHTML = ''
		for (let i = 0; i < 5; i++) {
			const d = new Date(today)
			d.setDate(today.getDate() + i)
			const el = document.createElement('div')
			el.className = 'rounded-md border border-slate-800 bg-slate-950 p-3 text-center'
			el.innerHTML = `
				<div class="font-semibold">${days[d.getDay()]}</div>
				<div class="text-3xl">${icons[randomInt(0, icons.length - 1)]}</div>
				<div class="text-sm text-slate-300">${randomInt(22, 36)}°C</div>
			`
			forecast.appendChild(el)
		}

		const soil = document.getElementById('soil-data')
		soil.innerHTML = ''
		const items = [
			{ label: 'pH', value: (Math.random() * 2 + 6).toFixed(1) },
			{ label: 'Nitrogen (N)', value: ['Low', 'Medium', 'High'][randomInt(0, 2)] },
			{ label: 'Phosphorus (P)', value: ['Low', 'Medium', 'High'][randomInt(0, 2)] },
			{ label: 'Potassium (K)', value: ['Low', 'Medium', 'High'][randomInt(0, 2)] }
		]
		items.forEach((it) => {
			const row = document.createElement('div')
			row.className = 'flex justify-between bg-slate-950 border border-slate-800 rounded-md p-2 text-sm'
			row.innerHTML = `<span>${it.label}</span><span class="text-slate-300">${it.value}</span>`
			soil.appendChild(row)
		})

		const alerts = document.getElementById('alerts')
		alerts.innerHTML = ''
		if (Math.random() > 0.5) {
			const li = document.createElement('li')
			li.textContent = 'Heavy rain expected in 48 hours. Prepare drainage.'
			alerts.appendChild(li)
		}
	}

	// Disease Detection (mock)
	function initDisease() {
		document.getElementById('disease-image').addEventListener('change', () => {
			const result = document.getElementById('disease-result')
			result.innerHTML = '<div class="animate-pulse">Analyzing image...</div>'
			setTimeout(() => {
				const diseases = [
					{ name: 'Leaf Blight', symptoms: 'Brown spots, wilting', treat: 'Copper fungicide; Neem spray' },
					{ name: 'Powdery Mildew', symptoms: 'White powder on leaves', treat: 'Sulfur spray; Milk solution' },
					{ name: 'Root Rot', symptoms: 'Yellowing, poor growth', treat: 'Improve drainage; Bio-fungicide' }
				]
				const pick = diseases[randomInt(0, diseases.length - 1)]
				result.innerHTML = `
					<div class="text-lg font-semibold">${pick.name}</div>
					<div class="text-sm text-slate-300">Symptoms: ${pick.symptoms}</div>
					<div class="text-sm text-slate-300">Treatment: ${pick.treat}</div>
				`
			}, 1000)
		})
	}

	// Market Prices
	const MARKET_DATA = {
		'Uttar Pradesh': {
			'Lucknow': {
				Hazratganj: { crops: ['Wheat', 'Rice', 'Pulses'], prices: { Wheat: [2100,2150,2170,2200,2180,2220,2250], Rice: [2500,2520,2480,2510,2530,2550,2580], Pulses: [6500,6400,6450,6550,6600,6580,6620] } }
			}
		},
		'Punjab': {
			'Amritsar': {
				Amritsar: { crops: ['Wheat', 'Rice', 'Maize'], prices: { Wheat: [2200,2220,2210,2230,2240,2260,2270], Rice: [2600,2580,2590,2610,2620,2630,2650], Maize: [1900,1920,1910,1930,1950,1960,1970] } }
			}
		},
		'Bihar': {
			'Patna': {
				'Patna City': { crops: ['Paddy', 'Maize', 'Wheat'], prices: { Paddy: [1800,1820,1810,1830,1840,1850,1860], Maize: [1700,1710,1720,1730,1740,1750,1760], Wheat: [2100,2110,2120,2130,2140,2150,2160] } }
			}
		},
		'West Bengal': {
			'Kolkata': {
				'Bara Bazar': { crops: ['Rice', 'Jute', 'Potato'], prices: { Rice: [2400,2410,2420,2430,2440,2460,2475], Jute: [5000,5050,5100,5200,5150,5220,5250], Potato: [1200,1220,1210,1230,1240,1250,1260] } }
			}
		}
	}

	function populateMarketSelectors() {
		const stateSel = document.getElementById('state-select')
		const districtSel = document.getElementById('district-select')
		const mandiSel = document.getElementById('mandi-select')
		const cropSel = document.getElementById('crop-select')

		function fillSelect(select, items) {
			select.innerHTML = '<option value="">--</option>' + items.map((v) => `<option value="${v}">${v}</option>`).join('')
		}

		fillSelect(stateSel, Object.keys(MARKET_DATA))
		districtSel.innerHTML = ''
		mandiSel.innerHTML = ''
		cropSel.innerHTML = ''

		stateSel.addEventListener('change', () => {
			const districts = Object.keys(MARKET_DATA[stateSel.value] || {})
			fillSelect(districtSel, districts)
			fillSelect(mandiSel, [])
			fillSelect(cropSel, [])
		})

		districtSel.addEventListener('change', () => {
			const mandis = Object.keys((MARKET_DATA[stateSel.value] || {})[districtSel.value] || {})
			fillSelect(mandiSel, mandis)
			fillSelect(cropSel, [])
		})

		mandiSel.addEventListener('change', () => {
			const mandi = (((MARKET_DATA[stateSel.value] || {})[districtSel.value] || {})[mandiSel.value] || {})
			fillSelect(cropSel, mandi.crops || [])
		})
	}

	function initMarket() {
		populateMarketSelectors()
		document.getElementById('load-prices').addEventListener('click', () => {
			const state = document.getElementById('state-select').value
			const district = document.getElementById('district-select').value
			const mandi = document.getElementById('mandi-select').value
			const crop = document.getElementById('crop-select').value
			if (!state || !district || !mandi || !crop) return
			const data = MARKET_DATA[state][district][mandi]
			const series = data.prices[crop]
			const ctx = document.getElementById('price-chart').getContext('2d')
			if (priceChartInstance) priceChartInstance.destroy()
			priceChartInstance = new Chart(ctx, {
				type: 'line',
				data: {
					labels: ['-6d','-5d','-4d','-3d','-2d','-1d','Today'],
					datasets: [{ label: `${mandi} - ${crop}`, data: series, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.2)', tension: 0.3 }]
				},
				options: { plugins: { legend: { labels: { color: '#cbd5e1' } } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.2)' } } } }
			})
			document.getElementById('market-summary').textContent = `Latest price for ${crop} at ${mandi}, ${district}, ${state}: ₹${series[series.length - 1].toLocaleString('en-IN')}/qtl`
		})
	}

	// Dashboard
	function initDashboard() {
		const history = [
			{ key: 'Location', value: 'Near Kanpur, UP' },
			{ key: 'Last crop', value: 'Wheat' },
			{ key: 'Soil test', value: 'pH 6.8, N-M, P-H, K-M' }
		]
		const ul = document.getElementById('farm-history')
		ul.innerHTML = ''
		history.forEach((h) => {
			const li = document.createElement('li')
			li.innerHTML = `<span class="text-slate-400">${h.key}:</span> ${h.value}`
			ul.appendChild(li)
		})

		const profit = document.getElementById('profitability')
		profit.innerHTML = ''
		const cards = [
			{ k: 'Revenue', v: `₹${randomInt(70000, 120000).toLocaleString('en-IN')}` },
			{ k: 'Costs', v: `₹${randomInt(30000, 60000).toLocaleString('en-IN')}` },
			{ k: 'Net Profit', v: `₹${randomInt(20000, 60000).toLocaleString('en-IN')}` }
		]
		cards.forEach((c) => {
			const d = document.createElement('div')
			d.className = 'rounded-md border border-slate-800 bg-slate-950 p-3'
			d.innerHTML = `<div class="text-xs text-slate-400">${c.k}</div><div class="text-lg font-semibold">${c.v}</div>`
			profit.appendChild(d)
		})

		// Todo list
		const todoInput = document.getElementById('todo-input')
		const todoAdd = document.getElementById('todo-add')
		const todoList = document.getElementById('todo-list')
		const todos = []
		function renderTodos() {
			todoList.innerHTML = ''
			todos.forEach((t, idx) => {
				const li = document.createElement('li')
				li.className = 'flex items-center justify-between bg-slate-950 border border-slate-800 rounded-md p-2 text-sm'
				li.innerHTML = `<span class="${t.done ? 'line-through text-slate-500' : ''}">${t.text}</span><div class="flex gap-2"><button data-act="toggle" data-idx="${idx}" class="px-2 py-1 rounded bg-emerald-600 text-white text-xs">${t.done ? 'Undo' : 'Done'}</button><button data-act="remove" data-idx="${idx}" class="px-2 py-1 rounded bg-red-600 text-white text-xs">Del</button></div>`
				todoList.appendChild(li)
			})
		}
		todoAdd.addEventListener('click', () => {
			const txt = todoInput.value.trim()
			if (!txt) return
			todos.push({ text: txt, done: false })
			todoInput.value = ''
			renderTodos()
		})
		todoList.addEventListener('click', (e) => {
			const btn = e.target.closest('button')
			if (!btn) return
			const idx = Number(btn.getAttribute('data-idx'))
			const act = btn.getAttribute('data-act')
			if (act === 'toggle') todos[idx].done = !todos[idx].done
			if (act === 'remove') todos.splice(idx, 1)
			renderTodos()
		})
		renderTodos()

		// Yield chart
		const yctx = document.getElementById('yield-chart').getContext('2d')
		if (yieldChartInstance) yieldChartInstance.destroy()
		yieldChartInstance = new Chart(yctx, {
			type: 'bar',
			data: {
				labels: ['Rabi 21', 'Kharif 22', 'Rabi 22', 'Kharif 23', 'Rabi 23'],
				datasets: [{ label: 'q/acre', data: [22, 28, 25, 30, 32], backgroundColor: '#6366f1' }]
			},
			options: { plugins: { legend: { labels: { color: '#cbd5e1' } } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.2)' } } } }
		})
	}

	// Chatbot
	function initChat() {
		const area = document.getElementById('chat-area')
		const input = document.getElementById('chat-input')
		const send = document.getElementById('chat-send')
		function appendBubble(text, from) {
			const div = document.createElement('div')
			div.className = `max-w-[80%] ${from === 'user' ? 'ml-auto' : ''}`
			div.innerHTML = `<div class="inline-block px-3 py-2 rounded-lg ${from === 'user' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-100'}">${text}</div>`
			area.appendChild(div)
			area.scrollTop = area.scrollHeight
		}
		function botReply(userText) {
			const typing = document.createElement('div')
			typing.className = 'text-slate-400 text-sm italic'
			typing.textContent = 'Bot is typing…'
			area.appendChild(typing)
			area.scrollTop = area.scrollHeight
			setTimeout(() => {
				typing.remove()
				const replies = [
					"Great question! Consider soil moisture before irrigation.",
					"Rotate crops to improve soil fertility.",
					"You can expect showers this week; plan accordingly.",
					"Use neem-based bio-pesticides for a safer approach."
				]
				appendBubble(replies[randomInt(0, replies.length - 1)], 'bot')
			}, 800)
		}
		send.addEventListener('click', () => {
			const txt = input.value.trim()
			if (!txt) return
			appendBubble(txt, 'user')
			input.value = ''
			botReply(txt)
		})
		input.addEventListener('keydown', (e) => {
			if (e.key === 'Enter') {
				send.click()
			}
		})
	}

	function initFooterYear() {
		document.getElementById('year').textContent = new Date().getFullYear()
	}

	function init() {
		initNav()
		initSuggestions()
		initWeatherSoil()
		initDisease()
		initMarket()
		initDashboard()
		initChat()
		initFooterYear()
		document.addEventListener('lang:changed', () => {
			// no-op for now; dynamic texts are minimal
		})
	}

	window.addEventListener('DOMContentLoaded', init)
})()


