import type { Config } from "tailwindcss";

export default {
	darkMode: ["class"],
	content: [
		"./pages/**/*.{ts,tsx}",
		"./components/**/*.{ts,tsx}",
		"./app/**/*.{ts,tsx}",
		"./src/**/*.{ts,tsx}",
	],
	prefix: "",
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px'
			}
		},
		extend: {
			fontFamily: {
				'sans': ['Inter', 'system-ui', 'sans-serif'],
				'mono': ['JetBrains Mono', 'Monaco', 'Cascadia Code', 'monospace'],
			},
			colors: {
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				
				sidebar: {
					bg: 'var(--sidebar-bg)',
					item: 'hsl(var(--sidebar-item))',
					active: 'var(--sidebar-active)',
					text: 'hsl(var(--sidebar-text))',
					border: 'hsl(var(--sidebar-border))'
				},
				
				chat: {
					bg: 'var(--chat-bg)',
					panel: 'var(--chat-panel)',
					border: 'hsl(var(--chat-border))',
					message: 'var(--chat-message)',
					user: 'var(--chat-user)',
					input: 'var(--chat-input)'
				},
				
				preview: {
					bg: 'hsl(var(--preview-bg))',
					border: 'hsl(var(--preview-border))',
					header: 'var(--preview-header)'
				},
				
				accent: {
					primary: 'hsl(var(--accent-primary))',
					secondary: 'hsl(var(--accent-secondary))',
					glow: 'hsl(var(--accent-glow))',
					soft: 'hsl(var(--accent-soft))'
				},
				
				text: {
					primary: 'hsl(var(--text-primary))',
					secondary: 'hsl(var(--text-secondary))',
					muted: 'hsl(var(--text-muted))',
					accent: 'hsl(var(--text-accent))'
				},
				
				success: 'hsl(var(--success))',
				warning: 'hsl(var(--warning))',
				error: 'hsl(var(--error))',
				info: 'hsl(var(--info))',
				
				glass: {
					bg: 'var(--glass-bg)',
					border: 'hsl(var(--glass-border))'
				}
			},
			borderRadius: {
				lg: 'var(--radius)',
				xl: 'var(--radius-xl)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)'
			},
			boxShadow: {
				'soft': 'var(--shadow-soft)',
				'medium': 'var(--shadow-medium)',
				'hard': 'var(--shadow-hard)',
				'glow': 'var(--shadow-glow)',
				'glow-strong': 'var(--shadow-glow-strong)',
				'glass': 'var(--glass-shadow)'
			},
			backdropBlur: {
				'xs': '2px',
				'glass': '12px'
			},
			transitionTimingFunction: {
				'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
			},
			keyframes: {
				'accordion-down': {
					from: {
						height: '0'
					},
					to: {
						height: 'var(--radix-accordion-content-height)'
					}
				},
				'accordion-up': {
					from: {
						height: 'var(--radix-accordion-content-height)'
					},
					to: {
						height: '0'
					}
				}
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out'
			}
		}
	},
	plugins: [require("tailwindcss-animate")],
} satisfies Config;
