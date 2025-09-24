// Basic multilingual dictionary and utilities
;(() => {
	const dictionaries = {
		en: {
			home: {
				title: 'Welcome to Crop Sense',
				subtitle: 'Smart, multilingual, responsive tools for Indian farmers.',
				cta: 'Start Crop Suggestion'
			},
			suggest: {
				title: 'Enter your details',
				soilType: 'Soil Type',
				location: 'Location',
				water: 'Water Availability',
				pastCrops: 'Past Crops',
				generate: 'Generate Suggestions',
				results: 'Top crop recommendations'
			},
			weather: {
				title: '5-day weather forecast'
			},
			soil: { title: 'Soil health' },
			alerts: { title: 'Alerts' },
			disease: {
				title: 'Upload crop image',
				hint: 'Clear photo of affected area works best.',
				resultTitle: 'Diagnosis'
			},
			market: {
				title: 'Market selection',
				state: 'State',
				district: 'District',
				mandi: 'Market',
				crop: 'Crop',
				load: 'Load Prices',
				trend: '7-day price trend'
			},
			dash: {
				farmHistory: 'Farm history',
				profitability: 'Profitability outlook',
				todo: 'To-Do',
				add: 'Add',
				yieldHistory: 'Yield history'
			},
			chat: { send: 'Send' }
		},
		hi: {
			home: {
				title: 'क्रॉप सेंस में आपका स्वागत है',
				subtitle: 'भारतीय किसानों के लिए स्मार्ट, बहुभाषी, उत्तरदायी उपकरण।',
				cta: 'फसल सुझाव शुरू करें'
			},
			suggest: {
				title: 'अपनी जानकारी दर्ज करें',
				soilType: 'मिट्टी का प्रकार',
				location: 'स्थान',
				water: 'पानी की उपलब्धता',
				pastCrops: 'पिछली फसलें',
				generate: 'सुझाव प्राप्त करें',
				results: 'शीर्ष फसल सुझाव'
			},
			weather: { title: '5-दिन का मौसम पूर्वानुमान' },
			soil: { title: 'मिट्टी स्वास्थ्य' },
			alerts: { title: 'चेतावनी' },
			disease: {
				title: 'फसल की तस्वीर अपलोड करें',
				hint: 'प्रभावित भाग की स्पष्ट तस्वीर सर्वोत्तम होती है।',
				resultTitle: 'निदान'
			},
			market: {
				title: 'मंडी चयन',
				state: 'राज्य',
				district: 'ज़िला',
				mandi: 'मंडी',
				crop: 'फसल',
				load: 'भाव देखें',
				trend: '7-दिन का भाव रुझान'
			},
			dash: {
				farmHistory: 'खेती इतिहास',
				profitability: 'लाभप्रदता दृष्टिकोण',
				todo: 'कार्य सूची',
				add: 'जोड़ें',
				yieldHistory: 'उपज इतिहास'
			},
			chat: { send: 'भेजें' }
		},
		// NOTE: For brevity, other languages map to Hindi for now; extend easily.
		kn: {}, te: {}, ta: {}, mr: {}, bn: {}, pa: {}, gu: {}, ml: {}, or: {}, as: {}, bh: {}, nj: {}
	}

	function deepGet(obj, path) {
		return path.split('.').reduce((acc, key) => (acc && acc[key] !== undefined ? acc[key] : undefined), obj)
	}

	function translatePage(lang) {
		const dict = { ...dictionaries.en, ...(dictionaries[lang] || {}) }
		document.querySelectorAll('[data-i18n]').forEach((el) => {
			const key = el.getAttribute('data-i18n')
			const val = deepGet(dict, key)
			if (typeof val === 'string') {
				el.textContent = val
			}
		})
	}

	function initI18n() {
		const select = document.getElementById('language-select')
		const saved = localStorage.getItem('cropSense.lang') || 'en'
		select.value = saved
		translatePage(saved)
		select.addEventListener('change', () => {
			const lang = select.value
			localStorage.setItem('cropSense.lang', lang)
			translatePage(lang)
			document.dispatchEvent(new CustomEvent('lang:changed', { detail: { lang } }))
		})
	}

	window.CropSenseI18N = { translatePage }
	window.addEventListener('DOMContentLoaded', initI18n)
})()


