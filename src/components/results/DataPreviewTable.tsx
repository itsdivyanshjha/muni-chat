import { useState } from 'react';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  ColumnDef,
  getPaginationRowModel,
} from '@tanstack/react-table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Download, Table2, ChevronLeft, ChevronRight, RefreshCw, Filter, FileSpreadsheet, Eye } from 'lucide-react';
import { DataPreview } from '@/lib/types';
import { toast } from '@/hooks/use-toast';

interface DataPreviewTableProps {
  dataPreview: DataPreview;
}

const pageSizeOptions = [
  { value: '10', label: '10 rows' },
  { value: '20', label: '20 rows' },
  { value: '50', label: '50 rows' },
  { value: '100', label: '100 rows' }
];

export function DataPreviewTable({ dataPreview }: DataPreviewTableProps) {
  const [data] = useState(() => {
    return dataPreview.rows.map(row => {
      const obj: any = {};
      dataPreview.columns.forEach((col, index) => {
        obj[col] = row[index];
      });
      return obj;
    });
  });
  const [pageSize, setPageSize] = useState('20');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const columns: ColumnDef<any>[] = dataPreview.columns.map(col => ({
    accessorKey: col,
    header: col,
    cell: ({ getValue }) => {
      const value = getValue();
      return <span className="font-mono text-sm">{String(value)}</span>;
    },
  }));

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: parseInt(pageSize),
      },
    },
  });

  const handleRefreshData = async () => {
    setIsRefreshing(true);
    // Simulate data refresh
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsRefreshing(false);
    toast({
      title: "Data refreshed",
      description: "Latest data has been loaded",
    });
  };

  const handleDownloadCSV = () => {
    const csvContent = [
      dataPreview.columns.join(','),
      ...dataPreview.rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'municipal-data.csv';
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: "Download started",
      description: "CSV file download has begun"
    });
  };

  return (
    <Card className="shadow-xl border-0 bg-gradient-to-br from-white to-blue-50">
      <CardHeader className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <CardTitle className="flex items-center gap-2">
            <FileSpreadsheet className="h-5 w-5" />
            Data Preview
          </CardTitle>
          
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
              <Eye className="h-3 w-3 mr-1" />
              {data.length} rows
            </Badge>
            
            <Select value={pageSize} onValueChange={setPageSize}>
              <SelectTrigger className="w-28 bg-white/20 border-white/30 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {pageSizeOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button
              variant="secondary"
              size="sm"
              onClick={handleRefreshData}
              disabled={isRefreshing}
              className="bg-white/20 border-white/30 text-white hover:bg-white/30"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={handleDownloadCSV}
              className="bg-white/20 border-white/30 text-white hover:bg-white/30"
            >
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div className="rounded-lg border overflow-hidden bg-white shadow-inner">
          <Table>
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id} className="bg-gradient-to-r from-gray-50 to-blue-50">
                  {headerGroup.headers.map((header) => (
                    <TableHead key={header.id} className="font-semibold text-gray-700 border-r border-gray-200 last:border-r-0">
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row, index) => (
                  <TableRow
                    key={row.id}
                    className={`hover:bg-blue-50 transition-colors ${
                      index % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'
                    }`}
                    data-state={row.getIsSelected() && "selected"}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id} className="border-r border-gray-100 last:border-r-0">
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={columns.length} className="h-32 text-center">
                    <div className="flex flex-col items-center gap-2 text-gray-500">
                      <Table2 className="h-8 w-8" />
                      <span>No data available</span>
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
        
        {/* Enhanced Pagination */}
        <div className="flex flex-col sm:flex-row items-center justify-between mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-600 mb-2 sm:mb-0">
            <span className="font-medium">
              Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{' '}
              {Math.min(
                (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
                data.length
              )}{' '}
              of {data.length} rows
            </span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Page size:</span>
              <Badge variant="outline" className="text-blue-600 border-blue-300">
                {pageSize} rows
              </Badge>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
                className="bg-white hover:bg-blue-50 border-blue-200"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              
              <Badge variant="secondary" className="px-3 py-1">
                Page {table.getState().pagination.pageIndex + 1} of{' '}
                {table.getPageCount()}
              </Badge>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
                className="bg-white hover:bg-blue-50 border-blue-200"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}