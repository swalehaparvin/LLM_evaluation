import { useState } from "react";
import { Link, useLocation } from "wouter";
import { 
  BarChart3, 
  Bot, 
  TestTube, 
  TrendingUp, 
  FileText, 
  Code, 
  Plus, 
  Download 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/", icon: BarChart3 },
  { name: "Models", href: "/models", icon: Bot },
  { name: "Test Suites", href: "/test-suites", icon: TestTube },
  { name: "Evaluations", href: "/evaluations", icon: TrendingUp },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "API", href: "/api", icon: Code },
];

const quickActions = [
  { name: "New Evaluation", icon: Plus },
  { name: "Export Results", icon: Download },
];

export default function Sidebar() {
  const [location] = useLocation();

  return (
    <aside className="w-64 bg-white shadow-sm border-r border-gray-200">
      <nav className="mt-8">
        <div className="px-4">
          <ul className="space-y-2">
            {navigation.map((item) => {
              const isActive = location === item.href;
              const Icon = item.icon;
              
              return (
                <li key={item.name}>
                  <Link href={item.href}>
                    <a className={cn(
                      "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-gray-700 hover:bg-gray-50"
                    )}>
                      <Icon className={cn(
                        "mr-3 h-5 w-5",
                        isActive ? "text-primary" : "text-gray-400"
                      )} />
                      {item.name}
                    </a>
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="mt-8 px-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Quick Actions
          </h3>
          <ul className="mt-4 space-y-2">
            {quickActions.map((item) => {
              const Icon = item.icon;
              
              return (
                <li key={item.name}>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-gray-700 hover:bg-gray-50"
                  >
                    <Icon className="mr-3 h-4 w-4 text-gray-400" />
                    {item.name}
                  </Button>
                </li>
              );
            })}
          </ul>
        </div>
      </nav>
    </aside>
  );
}
