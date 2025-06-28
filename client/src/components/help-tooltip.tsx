import { HelpCircle } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface HelpTooltipProps {
  content: string;
  className?: string;
}

const securityTips = [
  "🛡️ Fun fact: The first computer virus was created in 1971 and was called 'The Creeper'!",
  "🔒 Pro tip: Strong passwords are like good friends - long, complex, and hard to guess!",
  "🕵️ Security reminder: Social engineering attacks exploit human psychology, not just code!",
  "⚡ Did you know? The average time to detect a data breach is 197 days - prevention is key!",
  "🎭 Interesting: The term 'phishing' comes from 'fishing' - attackers cast nets hoping to catch victims!",
  "🧠 Memory safety tip: Buffer overflows have caused some of history's most famous security breaches!",
  "🌐 Global insight: Cybersecurity threats cross all borders - international cooperation is crucial!",
  "🔍 Testing wisdom: Red teams think like attackers to help blue teams defend better!",
  "🚀 Future-proofing: AI can both enhance security and create new attack vectors!",
  "🎯 Attack surface: Every line of code is a potential entry point - simplicity enhances security!"
];

export default function HelpTooltip({ content, className = "" }: HelpTooltipProps) {
  // Add a random security tip to the content
  const randomTip = securityTips[Math.floor(Math.random() * securityTips.length)];
  const enhancedContent = `${content}\n\n${randomTip}`;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <HelpCircle className={`h-4 w-4 text-gray-400 hover:text-blue-500 cursor-help transition-colors ${className}`} />
        </TooltipTrigger>
        <TooltipContent className="max-w-xs p-3 bg-white dark:bg-gray-800 border shadow-lg">
          <div className="whitespace-pre-line text-sm">
            {enhancedContent}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}