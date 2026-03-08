import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
    // 加载环境变量
    const env = loadEnv(mode, process.cwd())
    
    // 根据环境设置base路径
    const base = mode === 'production' ? '/srs/' : '/'
    
    return {
        plugins: [vue()],
        resolve: {
            alias: {
                '@': resolve(__dirname, 'src')
            }
        },
        server: {
            port: 3000,
            proxy: {
                '/api': {
                    target: 'http://localhost:12315',
                    changeOrigin: true
                }
            }
        },
        base: base,
        build: {
            outDir: '../static',
            emptyOutDir: true
        }
    }
})