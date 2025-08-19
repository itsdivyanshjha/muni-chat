import { useState } from 'react';
import { CalendarIcon, MapPin, Tag, X } from 'lucide-react';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { useFilters } from '@/stores/filters';
import { cn } from '@/lib/utils';

export function FilterBar() {
  const { filters, setTimeRange, setWard, setZone, setCategory, clearAll } = useFilters();
  const [dateFrom, setDateFrom] = useState<Date>();
  const [dateTo, setDateTo] = useState<Date>();

  const handleDateFromSelect = (date: Date | undefined) => {
    setDateFrom(date);
    const fromStr = date ? format(date, 'yyyy-MM-dd') : null;
    const toStr = dateTo ? format(dateTo, 'yyyy-MM-dd') : filters.time.to;
    setTimeRange(fromStr, toStr);
  };

  const handleDateToSelect = (date: Date | undefined) => {
    setDateTo(date);
    const fromStr = dateFrom ? format(dateFrom, 'yyyy-MM-dd') : filters.time.from;
    const toStr = date ? format(date, 'yyyy-MM-dd') : null;
    setTimeRange(fromStr, toStr);
  };

  const hasActiveFilters = 
    filters.time.from || 
    filters.time.to || 
    filters.place.ward || 
    filters.place.zone || 
    filters.extra.category;

  return (
    <div className="sticky top-16 z-10 bg-background/95 backdrop-blur border-b px-4 py-2 space-y-2">
      <div className="flex flex-wrap items-center gap-4">
        {/* Date Range */}
        <div className="flex items-center gap-2">
          <Label className="text-sm font-medium whitespace-nowrap">Date Range:</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-[130px] justify-start text-left font-normal",
                  !dateFrom && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {dateFrom ? format(dateFrom, "MMM dd") : "From"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={dateFrom}
                onSelect={handleDateFromSelect}
                initialFocus
                className="pointer-events-auto"
              />
            </PopoverContent>
          </Popover>

          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-[130px] justify-start text-left font-normal",
                  !dateTo && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {dateTo ? format(dateTo, "MMM dd") : "To"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={dateTo}
                onSelect={handleDateToSelect}
                initialFocus
                className="pointer-events-auto"
              />
            </PopoverContent>
          </Popover>
        </div>

        {/* Ward */}
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-muted-foreground" />
          <Select value={filters.place.ward || ""} onValueChange={setWard}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Ward" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ward-1">Ward 1</SelectItem>
              <SelectItem value="ward-2">Ward 2</SelectItem>
              <SelectItem value="ward-3">Ward 3</SelectItem>
              <SelectItem value="ward-4">Ward 4</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Zone */}
        <div className="flex items-center gap-2">
          <Select value={filters.place.zone || ""} onValueChange={setZone}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Zone" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="downtown">Downtown</SelectItem>
              <SelectItem value="residential">Residential</SelectItem>
              <SelectItem value="industrial">Industrial</SelectItem>
              <SelectItem value="commercial">Commercial</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Category */}
        <div className="flex items-center gap-2">
          <Tag className="h-4 w-4 text-muted-foreground" />
          <Select value={filters.extra.category || ""} onValueChange={setCategory}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="transportation">Transportation</SelectItem>
              <SelectItem value="public-safety">Public Safety</SelectItem>
              <SelectItem value="parks-recreation">Parks & Recreation</SelectItem>
              <SelectItem value="utilities">Utilities</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Clear Filters */}
        {hasActiveFilters && (
          <Button 
            variant="ghost" 
            size="sm"
            onClick={clearAll}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4 mr-1" />
            Clear All
          </Button>
        )}
      </div>
    </div>
  );
}