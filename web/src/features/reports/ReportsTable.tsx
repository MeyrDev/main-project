import type { ReportItem } from "./types";

type Props = {
  items: ReportItem[];
  onSelectReport: (reportId: string) => void;
};

export function ReportsTable({ items, onSelectReport }: Props) {
  if (items.length === 0) {
    return <p>Отчёты пока не созданы.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Название</th>
          <th>Тип</th>
          <th>Статус</th>
          <th>Дата создания</th>
          <th>Файл</th>
          <th>Действие</th>
        </tr>
      </thead>

      <tbody>
        {items.map((report) => (
          <tr key={report.id}>
            <td>{report.title}</td>
            <td>{report.report_type}</td>
            <td>{report.status}</td>
            <td>{new Date(report.created_at).toLocaleString()}</td>
            <td>{report.file_path ?? "JSON-отчёт"}</td>
            <td>
              <button className="button" onClick={() => onSelectReport(report.id)}>
                Открыть отчёт
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}