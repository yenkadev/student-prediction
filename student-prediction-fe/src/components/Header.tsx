import "./Header.css";

interface HeaderProps {
  title: string;
  subtitle: string;
}

export function Header({ title, subtitle }: HeaderProps) {
  return (
    <header className="page-header">
      <div>
        <div className="page-header__title">{title}</div>
        <div className="page-header__subtitle">{subtitle}</div>
      </div>
    </header>
  );
}
