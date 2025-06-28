import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Bot } from "lucide-react";
import { api, type LlmModel } from "@/lib/api";

interface ModelConfigProps {
  selectedModel: string;
  onModelChange: (modelId: string) => void;
  config: {
    temperature: number;
    maxTokens: number;
  };
  onConfigChange: (config: { temperature: number; maxTokens: number }) => void;
}

export default function ModelConfig({ 
  selectedModel, 
  onModelChange, 
  config, 
  onConfigChange 
}: ModelConfigProps) {
  const { data: models } = useQuery<LlmModel[]>({
    queryKey: ['/api/models'],
  });

  const handleTemperatureChange = (value: number[]) => {
    onConfigChange({ ...config, temperature: value[0] });
  };

  const handleMaxTokensChange = (value: string) => {
    const maxTokens = parseInt(value);
    if (!isNaN(maxTokens)) {
      onConfigChange({ ...config, maxTokens });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Bot className="h-5 w-5 mr-2 text-primary" />
          Model Configuration
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label>Select Model</Label>
          <Select value={selectedModel} onValueChange={onModelChange}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a model..." />
            </SelectTrigger>
            <SelectContent>
              {models?.map((model) => (
                <SelectItem key={model.modelId} value={model.modelId}>
                  {model.name} ({model.provider})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label>Temperature: {config.temperature}</Label>
          <Slider
            value={[config.temperature]}
            onValueChange={handleTemperatureChange}
            max={1}
            min={0}
            step={0.1}
            className="mt-2"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0.0</span>
            <span>1.0</span>
          </div>
        </div>

        <div>
          <Label>Max Tokens</Label>
          <Input
            type="number"
            value={config.maxTokens}
            onChange={(e) => handleMaxTokensChange(e.target.value)}
            min={1}
            max={4000}
          />
        </div>
      </CardContent>
    </Card>
  );
}
