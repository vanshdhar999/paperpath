"use client";

interface ContributionGridProps {
  contributions: Record<string, number>;
}

export default function ContributionGrid({ contributions }: ContributionGridProps) {
  // Generate last 365 days
  const today = new Date();
  const days: Date[] = [];
  for (let i = 364; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    days.push(d);
  }

  // Group by week
  const weeks: Date[][] = [];
  let currentWeek: Date[] = [];
  days.forEach((day) => {
    if (day.getDay() === 0 && currentWeek.length > 0) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
    currentWeek.push(day);
  });
  if (currentWeek.length > 0) weeks.push(currentWeek);

  function getColor(count: number): string {
    if (count === 0) return "bg-gray-800";
    if (count === 1) return "bg-green-900";
    if (count === 2) return "bg-green-700";
    if (count === 3) return "bg-green-500";
    return "bg-green-400";
  }

  const monthLabels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  return (
    <div>
      <div className="flex gap-0.5 overflow-x-auto">
        {weeks.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-0.5">
            {week.map((day) => {
              const dateStr = day.toISOString().split("T")[0];
              const count = contributions[dateStr] || 0;
              return (
                <div
                  key={dateStr}
                  className={`w-3 h-3 rounded-sm ${getColor(count)}`}
                  title={`${dateStr}: ${count} paper${count !== 1 ? "s" : ""}`}
                />
              );
            })}
          </div>
        ))}
      </div>
      <div className="flex justify-between mt-2 text-xs text-gray-500">
        {monthLabels.map((m) => (
          <span key={m}>{m}</span>
        ))}
      </div>
      <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
        <span>Less</span>
        <div className="w-3 h-3 rounded-sm bg-gray-800" />
        <div className="w-3 h-3 rounded-sm bg-green-900" />
        <div className="w-3 h-3 rounded-sm bg-green-700" />
        <div className="w-3 h-3 rounded-sm bg-green-500" />
        <div className="w-3 h-3 rounded-sm bg-green-400" />
        <span>More</span>
      </div>
    </div>
  );
}
