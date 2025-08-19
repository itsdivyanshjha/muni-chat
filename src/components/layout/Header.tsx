import { Building2, Moon, Sun, User, Settings, LogOut, Activity, TrendingUp, BarChart3, Sparkles, Globe, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useTheme } from '@/hooks/use-theme';
import { colors, gradients } from '@/lib/colors';

export function Header() {
  const { theme, setTheme } = useTheme();

  return (
    <header 
      className="sticky top-0 z-50 w-full border-b-2 border-purple-500/20 backdrop-blur-md overflow-hidden"
      style={{ 
        background: gradients.primary,
        boxShadow: '0 8px 32px rgba(16, 0, 43, 0.3)'
      }}
    >
      {/* Animated Background Elements */}
      <div className="absolute inset-0 opacity-10 pointer-events-none">
        <div className="absolute top-4 left-1/4 animate-pulse">
          <BarChart3 className="h-8 w-8 text-white" />
        </div>
        <div className="absolute top-8 right-1/3 animate-bounce" style={{ animationDelay: '1s' }}>
          <TrendingUp className="h-6 w-6 text-white" />
        </div>
        <div className="absolute bottom-4 left-1/3 animate-pulse" style={{ animationDelay: '2s' }}>
          <Globe className="h-7 w-7 text-white" />
        </div>
        <div className="absolute top-12 right-1/4 animate-pulse" style={{ animationDelay: '0.5s' }}>
          <Zap className="h-5 w-5 text-white" />
        </div>
      </div>
      
      <div className="relative container flex h-24 items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <div 
            className="flex h-14 w-14 items-center justify-center rounded-2xl shadow-xl backdrop-blur-sm border border-white/20"
            style={{ 
              background: 'rgba(255, 255, 255, 0.15)'
            }}
          >
            <Building2 className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">
              Municipal AI Insights
            </h1>
            <p className="text-lg text-blue-100 font-medium">
              AI-Powered Government Data Analytics Platform
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex flex-col items-end">
            <div className="text-white/90 text-sm font-semibold">25+ Datasets</div>
            <div className="text-blue-200 text-xs">Real-time Analytics</div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            className="h-12 w-12 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20"
          >
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0 text-white" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100 text-white" />
            <span className="sr-only">Toggle theme</span>
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="secondary" 
                size="lg"
                className="bg-white/20 text-white border-white/30 hover:bg-white/30 backdrop-blur-sm font-semibold shadow-lg"
              >
                <User className="h-4 w-4 mr-2" />
                Dashboard
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 bg-white/95 backdrop-blur-md border border-purple-200">
              <DropdownMenuItem className="cursor-pointer">
                <User className="h-4 w-4 mr-2" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer text-red-600">
                <LogOut className="h-4 w-4 mr-2" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      
      {/* Bottom accent line */}
      <div 
        className="h-1"
        style={{ 
          background: `linear-gradient(90deg, ${colors.vividSkyBlue}, ${colors.pacificCyan}, ${colors.blueGreen}, ${colors.honoluluBlue})`
        }}
      />
    </header>
  );
}