import React, {
  useEffect,
  useState,
  useRef,
  createContext,
  useContext,
} from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  Link,
  NavLink,
  Routes,
  Route,
  useParams,
  useNavigate,
} from "react-router-dom";
import "./styles.css";
import "./learning.css";
type Row = Record<string, any>;
async function api(path: string, method = "GET", body?: unknown) {
  const r = await fetch("/api" + path, {
    method,
    credentials: "same-origin",
    keepalive: path.endsWith("/watch"),
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const d = await r
    .json()
    .catch(() => ({ detail: "Некорректный ответ сервера" }));
  if (!r.ok)
    throw Error(
      typeof d.detail === "string" ? d.detail : "Проверьте поля формы",
    );
  return d;
}
function useLoad(path: string | null) {
  const [data, setData] = useState<any>(null),
    [error, setError] = useState(""),
    [v, setV] = useState(0);
  useEffect(() => {
    let active = true;
    if (!path) {
      setData(null);
      setError("");
      return;
    }
    setData(null);
    setError("");
    api(path)
      .then((d) => {
        if (active) setData(d);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [path, v]);
  return { data, error, reload: () => setV((x) => x + 1) };
}
const UserContext = createContext<Row | null>(null);
function Heading({ title, text = "" }: { title: string; text?: string }) {
  return (
    <div className="page-heading">
      <span className="eyebrow">УЧЕБНАЯ МАСТЕРСКАЯ</span>
      <h1>{title}</h1>
      <p>{text}</p>
    </div>
  );
}
function State({ data, error }: { data: any; error: string }) {
  return error ? (
    <p className="notice" role="alert">
      {error}
    </p>
  ) : data === null ? (
    <p role="status">Загрузка…</p>
  ) : null;
}
function DateText({ value }: { value: any }) {
  return (
    <>{value ? new Date(value).toLocaleString("ru-RU") : "Нет активности"}</>
  );
}
function Progress({ p }: { p: Row }) {
  return (
    <>
      <strong>
        {p.completed} / {p.total} уроков · {p.percent}%
      </strong>
      <progress value={p.percent} max={100} />
      {p.demo && <small className="pill">Тестовые показатели</small>}
    </>
  );
}
function Denied() {
  return (
    <section className="panel">
      <h2>Нет доступа</h2>
      <p>Войдите под пользователем с нужными правами.</p>
      <Link to="/login">Войти →</Link>
    </section>
  );
}
function Guard({
  children,
  staff = false,
}: {
  children: React.ReactNode;
  staff?: boolean;
}) {
  const u = useContext(UserContext);
  return !u || (staff && !["teacher", "admin"].includes(u.role)) ? (
    <Denied />
  ) : (
    <>{children}</>
  );
}
function App() {
  const [user, setUser] = useState<Row | null>(null),
    [ready, setReady] = useState(false),
    [error, setError] = useState("");
  useEffect(() => {
    api("/me")
      .then(setUser)
      .catch(() => {})
      .finally(() => setReady(true));
  }, []);
  const teacher = user && ["teacher", "admin"].includes(user.role);
  return (
    <UserContext.Provider value={user}>
      <BrowserRouter>
        <div className="shell">
          <aside className="sidebar">
            <Link className="brand" to="/">
              <span className="brand-icon">м.</span>
              <span>
                Mini LMS<small>учебная мастерская</small>
              </span>
            </Link>
            <p className="nav-label">МОЁ ПРОСТРАНСТВО</p>
            <nav>
              <NavLink to="/courses">Курсы</NavLink>
              {user && (
                <>
                  <NavLink to="/my">Моё обучение</NavLink>
                  <NavLink to="/grades">Мои оценки</NavLink>
                  <NavLink to="/profile">Профиль</NavLink>
                </>
              )}
              {teacher && (
                <>
                  <NavLink to="/teacher">Материалы</NavLink>
                  <NavLink to="/teacher/students">Ученики</NavLink>
                  <NavLink to="/teacher/grades">Оценки</NavLink>
                </>
              )}
              {user?.role === "admin" && (
                <NavLink to="/admin">Пользователи</NavLink>
              )}
            </nav>
            <div className="sidebar-bottom">
              <p>
                {user
                  ? `${user.display_name} · ${user.role}`
                  : "Каталог открыт для всех"}
              </p>
              {user ? (
                <button
                  className="button secondary"
                  onClick={async () => {
                    try {
                      await api("/auth/logout", "POST");
                      setUser(null);
                    } catch (e) {
                      setError((e as Error).message);
                    }
                  }}
                >
                  Выйти
                </button>
              ) : (
                <Link className="button" to="/login">
                  Войти
                </Link>
              )}
            </div>
          </aside>
          <div className="workspace">
            <header className="topbar">
              <span>Пространство для новых знаний</span>
              <span className="pill">PostgreSQL · учебные данные</span>
            </header>
            <main>
              {error && <p role="alert">{error}</p>}
              {!ready ? (
                <p>Проверяем сессию…</p>
              ) : (
                <Routes>
                  <Route path="/" element={<Catalog />} />
                  <Route path="/courses" element={<Catalog />} />
                  <Route path="/login" element={<Login onLogin={setUser} />} />
                  <Route
                    path="/my"
                    element={
                      <Guard>
                        <MyCourses />
                      </Guard>
                    }
                  />
                  <Route
                    path="/courses/:courseId"
                    element={
                      <Guard>
                        <CourseView />
                      </Guard>
                    }
                  />
                  <Route
                    path="/courses/:courseId/lessons/:lessonId"
                    element={
                      <Guard>
                        <LessonView />
                      </Guard>
                    }
                  />
                  <Route
                    path="/grades"
                    element={
                      <Guard>
                        <OwnGrades />
                      </Guard>
                    }
                  />
                  <Route
                    path="/profile"
                    element={
                      <Guard>
                        <Profile onChange={setUser} />
                      </Guard>
                    }
                  />
                  <Route
                    path="/teacher"
                    element={
                      <Guard staff>
                        <Materials />
                      </Guard>
                    }
                  />
                  <Route
                    path="/teacher/students"
                    element={
                      <Guard staff>
                        <Students />
                      </Guard>
                    }
                  />
                  <Route
                    path="/teacher/grades"
                    element={
                      <Guard staff>
                        <TeacherGrades />
                      </Guard>
                    }
                  />
                  <Route
                    path="/admin"
                    element={user?.role === "admin" ? <Admin /> : <Denied />}
                  />
                  <Route
                    path="*"
                    element={<Heading title="Страница не найдена" />}
                  />
                </Routes>
              )}
            </main>
            <footer>
              Mini LMS · Учебная мастерская{" "}
              <span>Результаты сохраняются. Тестовые записи подписаны.</span>
            </footer>
          </div>
        </div>
      </BrowserRouter>
    </UserContext.Provider>
  );
}
function Login({ onLogin }: { onLogin: (u: Row) => void }) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  return (
    <>
      <Heading
        title="Рады видеть вас снова."
        text="Войдите, чтобы открыть свои уроки и результаты."
      />
      <form
        className="panel auth"
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          setError("");
          const f = new FormData(e.currentTarget);
          try {
            onLogin(
              await api("/auth/login", "POST", {
                email: f.get("email"),
                password: f.get("password"),
              }),
            );
            navigate("/my");
          } catch (e) {
            setError((e as Error).message);
          } finally {
            setBusy(false);
          }
        }}
      >
        <label>
          Email
          <input name="email" type="email" autoComplete="username" required />
        </label>
        <label>
          Пароль
          <input
            name="password"
            type="password"
            autoComplete="current-password"
            required
          />
        </label>
        <button className="button" disabled={busy}>
          {busy ? "Входим…" : "Войти"}
        </button>
        {error && <p role="alert">{error}</p>}
        <p className="micro">
          Самостоятельная регистрация пока не подключена. Используйте выданный
          учебный аккаунт.
        </p>
      </form>
    </>
  );
}
function Catalog() {
  const { data, error } = useLoad("/courses");
  const [q, setQ] = useState("");
  const filtered = data?.filter((c: Row) =>
    c.title.toLowerCase().includes(q.toLowerCase()),
  );
  return (
    <>
      <Heading
        title="Найдите свою следующую идею."
        text="Опубликованные курсы. Уроки доступны после входа и зачисления."
      />
      <label className="search">
        Поиск курса
        <input value={q} onChange={(e) => setQ(e.target.value)} type="search" />
      </label>
      <State data={data} error={error} />
      <div className="course-grid">
        {filtered?.map((c: Row, i: number) => (
          <Link className="course-card" key={c.id} to={`/courses/${c.id}`}>
            <div
              className={"course-art " + ["mint", "peach", "lavender"][i % 3]}
            >
              <b>{String(i + 1).padStart(2, "0")} / ↗</b>
            </div>
            <div className="course-body">
              <span className="eyebrow">
                {c.lessons} уроков · {c.teacher}
              </span>
              <h3>{c.title}</h3>
              <p>{c.description}</p>
            </div>
          </Link>
        ))}
      </div>
      {filtered?.length === 0 && <p>Курсов не найдено.</p>}
    </>
  );
}
function MyCourses() {
  const { data, error } = useLoad("/me/courses");
  return (
    <>
      <Heading
        title="Моё обучение"
        text="Прогресс курса — доля завершённых уроков."
      />
      <State data={data} error={error} />
      {data?.length === 0 && <p>Вы пока не зачислены ни на один курс.</p>}
      {data?.map((c: Row) => (
        <section className="panel spaced" key={c.id}>
          <h2>
            <Link to={`/courses/${c.id}`}>{c.title} →</Link>
          </h2>
          <Progress p={c.progress} />
          <p>
            Последняя активность: <DateText value={c.progress.last_activity} />
          </p>
        </section>
      ))}
    </>
  );
}
function CourseView() {
  const { courseId } = useParams();
  const { data: c, error } = useLoad("/courses/" + courseId);
  return (
    <>
      <State data={c} error={error} />
      {c && (
        <>
          <Heading title={c.title} text={c.description} />
          <section className="panel">
            <Progress p={c.progress} />
            {c.modules.map((m: Row) => (
              <section key={m.id}>
                <h2>
                  {m.position}. {m.title}
                </h2>
                {c.items
                  .filter((l: Row) => l.module_id === m.id)
                  .map((l: Row) => (
                    <div className="lesson-row" key={l.id}>
                      <span>{l.position}</span>
                      <div>
                        <Link to={`/courses/${c.id}/lessons/${l.id}`}>
                          <strong>{l.title}</strong>
                        </Link>
                        <p className="micro">{l.summary}</p>
                        <span>
                          {l.duration_minutes} мин ·{" "}
                          {l.video ? "Видео" : "Текст"} · {l.status}
                        </span>
                        {l.demo && (
                          <span className="pill">Тестовый прогресс</span>
                        )}
                      </div>
                    </div>
                  ))}
              </section>
            ))}
          </section>
        </>
      )}
    </>
  );
}
function TrackedVideo({
  lesson,
  onProgress,
}: {
  lesson: Row;
  onProgress: (p: Row) => void;
}) {
  const video = useRef<HTMLVideoElement>(null),
    last = useRef<{ time: number; wall: number } | null>(null),
    pending = useRef<[number, number] | null>(null),
    chain = useRef(Promise.resolve());
  const [error, setError] = useState("");
  function flush() {
    const span = pending.current;
    pending.current = null;
    if (!span || span[1] - span[0] < 0.05) return;
    chain.current = chain.current.then(async () => {
      try {
        onProgress(
          await api(`/lessons/${lesson.id}/watch`, "POST", {
            start: span[0],
            end: span[1],
          }),
        );
        setError("");
      } catch (e) {
        setError((e as Error).message);
      }
    });
  }
  function reset() {
    flush();
    last.current = null;
  }
  function tick() {
    const v = video.current!,
      wall = performance.now() / 1000;
    if (v.paused || v.seeking || document.hidden) {
      reset();
      return;
    }
    const prev = last.current;
    last.current = { time: v.currentTime, wall };
    if (!prev) return;
    const delta = v.currentTime - prev.time,
      elapsed = wall - prev.wall;
    if (delta <= 0 || delta > Math.min(2, elapsed * v.playbackRate + 0.2)) {
      flush();
      return;
    }
    if (!pending.current) pending.current = [prev.time, v.currentTime];
    else pending.current[1] = v.currentTime;
    if (pending.current[1] - pending.current[0] >= 4) flush();
  }
  useEffect(() => {
    function hidden() {
      if (document.hidden) reset();
    }
    document.addEventListener("visibilitychange", hidden);
    return () => {
      document.removeEventListener("visibilitychange", hidden);
      reset();
    };
  }, [lesson.id]);
  return (
    <>
      <video
        ref={video}
        src={lesson.video_url}
        controls
        preload="metadata"
        onTimeUpdate={tick}
        onSeeking={reset}
        onSeeked={() => {
          last.current = null;
        }}
        onPause={reset}
        onEnded={reset}
        onPlay={() => {
          last.current = null;
        }}
        onRateChange={reset}
        onError={() =>
          setError(
            "Видео недоступно или источник не поддерживает HTML5. Прогресс не начисляется.",
          )
        }
      />
      <p className="micro">
        Завершение после 90% уникального просмотра. Перемотка не добавляет
        проценты.
      </p>
      {error && <p role="alert">{error}</p>}
    </>
  );
}
function LessonView() {
  const { lessonId } = useParams();
  const { data: l, error, reload } = useLoad("/lessons/" + lessonId);
  const [message, setMessage] = useState(""),
    [p, setP] = useState<Row | null>(null),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    setP(null);
    setMessage("");
  }, [lessonId]);
  return (
    <>
      <State data={l} error={error} />
      {l && (
        <>
          <Link to={`/courses/${l.course_id}`}>← К курсу</Link>
          <Heading
            title={l.title}
            text={`${l.duration_minutes} мин · ${l.summary}`}
          />
          <article className="panel prose">
            <p>
              {(p || l).status}
              {(p || l).demo ? " · Тестовый прогресс" : ""}
            </p>
            {l.video_url ? (
              <>
                <TrackedVideo key={l.id} lesson={l} onProgress={setP} />
                <p>Просмотрено: {(p || l).video_percent ?? 0}%</p>
              </>
            ) : (
              <p className="micro">Текстовый урок. Видео не добавлено.</p>
            )}
            <div className="lesson-content">{l.content}</div>
            <h2>Практика</h2>
            <p>
              {l.practice || "Повтори пример из урока и объясни результат."}
            </p>
            {!l.video_url && (
              <button
                className="button"
                disabled={busy || Boolean((p || l).completed && !(p || l).demo)}
                onClick={async () => {
                  setBusy(true);
                  try {
                    await api(`/lessons/${l.id}/complete`, "POST");
                    setMessage("Урок завершён. Прогресс сохранён.");
                    reload();
                  } catch (e) {
                    setMessage((e as Error).message);
                  } finally {
                    setBusy(false);
                  }
                }}
              >
                Завершить урок
              </button>
            )}
            <p role="status">{message}</p>
          </article>
        </>
      )}
    </>
  );
}
function GradesTable({ items }: { items: Row[] }) {
  return items.length ? (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Курс / урок</th>
            <th>Тип</th>
            <th>Оценка</th>
            <th>Комментарий</th>
            <th>Автор / изменение</th>
          </tr>
        </thead>
        <tbody>
          {items.map((g) => (
            <tr key={g.id}>
              <td>
                {g.course}
                <br />
                {g.lesson || "Итог за курс"}
              </td>
              <td>
                {
                  (
                    {
                      course: "Итог",
                      lesson: "Урок",
                      practice: "Практика",
                    } as Row
                  )[g.kind]
                }
              </td>
              <td>
                <strong>
                  {g.score === null ? "Не выставлена" : `${g.score} / 100`}
                </strong>
                {g.demo && <small> · Тестовая</small>}
              </td>
              <td>{g.comment || "—"}</td>
              <td>
                {g.author || "—"}
                <br />
                {g.updated_at ? <DateText value={g.updated_at} /> : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  ) : (
    <p>Не выставлена — оценок пока нет.</p>
  );
}
function OwnGrades() {
  const { data, error } = useLoad("/me/gradebook");
  return (
    <>
      <Heading
        title="Мои оценки"
        text="Шкала 0–100. Ноль — выставленная оценка, отдельно от отсутствия оценки."
      />
      <State data={data} error={error} />
      {data && (
        <section className="panel">
          <GradesTable items={data} />
        </section>
      )}
    </>
  );
}
function Profile({ onChange }: { onChange: (u: Row) => void }) {
  const user = useContext(UserContext)!;
  const [message, setMessage] = useState("");
  return (
    <>
      <Heading title="Мой профиль" text={`${user.email} · ${user.role}`} />
      <form
        className="panel editor"
        onSubmit={async (e) => {
          e.preventDefault();
          const f = new FormData(e.currentTarget);
          try {
            onChange(
              await api("/me", "PATCH", {
                display_name: f.get("display_name"),
                bio: f.get("bio"),
              }),
            );
            setMessage("Сохранено");
          } catch (e) {
            setMessage((e as Error).message);
          }
        }}
      >
        <label>
          Имя
          <input
            name="display_name"
            defaultValue={user.display_name}
            maxLength={100}
            required
          />
        </label>
        <label>
          О себе
          <textarea name="bio" defaultValue={user.bio} maxLength={500} />
        </label>
        <button className="button">Сохранить</button>
        <p role="status">{message}</p>
      </form>
    </>
  );
}
function Students() {
  const courses = useLoad("/staff/courses");
  const [cid, setCid] = useState(""),
    [q, setQ] = useState(""),
    [selection, setSelection] = useState<Row | null>(null);
  const { data, error } = useLoad(
    "/staff/students?" +
      new URLSearchParams({ ...(cid ? { course_id: cid } : {}), q }),
  );
  return (
    <>
      <Heading
        title="Ученики"
        text="Ученики ваших курсов. Демонстрационная активность отмечена отдельно."
      />
      <div className="toolbar">
        <label>
          Поиск по имени
          <input value={q} onChange={(e) => setQ(e.target.value)} />
        </label>
        <label>
          Курс
          <select
            value={cid}
            onChange={(e) => {
              setCid(e.target.value);
              setSelection(null);
            }}
          >
            <option value="">Все мои курсы</option>
            {courses.data?.map((c: Row) => (
              <option key={c.id} value={c.id}>
                {c.title}
              </option>
            ))}
          </select>
        </label>
      </div>
      <State data={data} error={error || courses.error} />
      {data && (
        <section className="panel table-wrap">
          <table>
            <thead>
              <tr>
                <th>Ученик</th>
                <th>Курс</th>
                <th>Уроки / прогресс</th>
                <th>Активность</th>
              </tr>
            </thead>
            <tbody>
              {data.map((r: Row) => (
                <tr key={r.user_id + "-" + r.course_id}>
                  <td>
                    <button
                      className="text-button"
                      onClick={() => setSelection(r)}
                    >
                      {r.name} →
                    </button>
                  </td>
                  <td>{r.course}</td>
                  <td>
                    {r.completed}/{r.total} · {r.percent}%{" "}
                    {r.demo && <small>Тестовые</small>}
                  </td>
                  <td>
                    <DateText value={r.last_activity} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!data.length && <p>Ученики не найдены.</p>}
        </section>
      )}
      {selection && (
        <StudentDetail
          key={selection.course_id + "-" + selection.user_id}
          row={selection}
        />
      )}
    </>
  );
}
function StudentDetail({ row }: { row: Row }) {
  const { data, error } = useLoad(
    `/staff/courses/${row.course_id}/students/${row.user_id}`,
  );
  return (
    <section className="panel spaced">
      <h2>
        {row.name} · {row.course}
      </h2>
      <State data={data} error={error} />
      {data && (
        <>
          <Progress p={data} />
          {data.lessons.map((l: Row) => (
            <div className="lesson-row" key={l.id}>
              <strong>{l.title}</strong>
              <span>
                {l.status} ·{" "}
                {l.video ? `${l.video_percent ?? 0}% видео` : "Текст"}{" "}
                {l.demo ? "· Тестовые данные" : ""}
              </span>
            </div>
          ))}
          <h3>Оценки</h3>
          <GradesTable items={data.grades} />
        </>
      )}
    </section>
  );
}
function TeacherGrades() {
  const courses = useLoad("/staff/courses");
  const [cid, setCid] = useState("");
  return (
    <>
      <Heading
        title="Оценки"
        text="Оценка урока, практики или итог за курс. Изменение сохраняет автора и время."
      />
      <State data={courses.data} error={courses.error} />
      <label>
        Курс
        <select value={cid} onChange={(e) => setCid(e.target.value)}>
          <option value="">Выберите курс</option>
          {courses.data?.map((c: Row) => (
            <option key={c.id} value={c.id}>
              {c.title}
            </option>
          ))}
        </select>
      </label>
      {cid && <GradeEditor key={cid} cid={cid} />}
    </>
  );
}
function GradeEditor({ cid }: { cid: string }) {
  const students = useLoad("/staff/students?course_id=" + cid),
    course = useLoad("/courses/" + cid);
  const [uid, setUid] = useState(""),
    [kind, setKind] = useState("course"),
    [lid, setLid] = useState(""),
    [message, setMessage] = useState(""),
    [version, setVersion] = useState(0);
  const detail = useLoad(uid ? `/staff/courses/${cid}/students/${uid}` : null);
  const [score, setScore] = useState(""),
    [comment, setComment] = useState("");
  useEffect(() => {
    const existing = detail.data?.grades.find(
      (g: Row) =>
        g.kind === kind &&
        (kind === "course"
          ? g.lesson_id === null
          : String(g.lesson_id) === lid),
    );
    setScore(existing ? String(existing.score) : "");
    setComment(existing?.comment || "");
  }, [uid, kind, lid, detail.data]);

  return (
    <section className="panel spaced">
      <State data={students.data} error={students.error || course.error} />
      <form
        className="editor"
        onSubmit={async (e) => {
          e.preventDefault();
          const f = new FormData(e.currentTarget);
          try {
            await api(`/staff/courses/${cid}/grades`, "PUT", {
              user_id: Number(uid),
              lesson_id: kind === "course" ? null : Number(lid),
              kind,
              score: Number(f.get("score")),
              comment: f.get("comment"),
            });
            setMessage("Оценка сохранена");
            setVersion((v) => v + 1);
            detail.reload();
          } catch (e) {
            setMessage((e as Error).message);
          }
        }}
      >
        <label>
          Ученик
          <select value={uid} required onChange={(e) => setUid(e.target.value)}>
            <option value="">Выберите ученика</option>
            {students.data?.map((s: Row) => (
              <option key={s.user_id} value={s.user_id}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Тип
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            <option value="course">Итог за курс</option>
            <option value="lesson">Урок</option>
            <option value="practice">Практика</option>
          </select>
        </label>
        {kind !== "course" && (
          <label>
            Урок
            <select
              value={lid}
              required
              onChange={(e) => setLid(e.target.value)}
            >
              <option value="">Выберите урок</option>
              {course.data?.items.map((l: Row) => (
                <option key={l.id} value={l.id}>
                  {l.title}
                </option>
              ))}
            </select>
          </label>
        )}
        <label>
          Оценка 0–100
          <input
            name="score"
            value={score}
            onChange={(e) => setScore(e.target.value)}
            type="number"
            min={0}
            max={100}
            step={1}
            required
          />
        </label>
        <label>
          Комментарий
          <textarea
            name="comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            maxLength={2000}
          />
        </label>
        <button className="button" disabled={!uid}>
          Сохранить / изменить оценку
        </button>
        <p role="status">{message}</p>
      </form>
      {uid && (
        <StudentDetail
          key={uid + "-" + version}
          row={{
            user_id: uid,
            course_id: cid,
            name: students.data?.find((s: Row) => String(s.user_id) === uid)
              ?.name,
            course: course.data?.title,
          }}
        />
      )}
    </section>
  );
}
function Materials() {
  const { data, error, reload } = useLoad("/staff/courses");
  const [chosen, setChosen] = useState("");
  return (
    <>
      <Heading
        title="Материалы мастерской"
        text="Управление своими курсами, модулями и уроками."
      />
      <State data={data} error={error} />
      <label>
        Курс
        <select value={chosen} onChange={(e) => setChosen(e.target.value)}>
          <option value="">Новый курс</option>
          {data?.map((c: Row) => (
            <option key={c.id} value={c.id}>
              {c.title}
            </option>
          ))}
        </select>
      </label>
      <CourseEditor
        key={chosen + JSON.stringify(data)}
        course={data?.find((c: Row) => String(c.id) === chosen)}
        onSave={reload}
      />
      {chosen && <ContentEditor key={chosen} cid={chosen} />}
    </>
  );
}
function CourseEditor({
  course: c,
  onSave,
}: {
  course?: Row;
  onSave: () => void;
}) {
  const [message, setMessage] = useState("");
  return (
    <form
      className="panel editor spaced"
      onSubmit={async (e) => {
        e.preventDefault();
        const f = new FormData(e.currentTarget);
        try {
          await api(
            "/staff/courses" + (c ? "/" + c.id : ""),
            c ? "PUT" : "POST",
            Object.fromEntries(f),
          );
          onSave();
          setMessage("Сохранено");
        } catch (e) {
          setMessage((e as Error).message);
        }
      }}
    >
      <h2>{c ? "Параметры курса" : "Создать курс"}</h2>
      <label>
        Название
        <input name="title" required maxLength={200} defaultValue={c?.title} />
      </label>
      <label>
        Адрес (латиница и дефисы)
        <input
          name="slug"
          required
          pattern="[a-z0-9]+(-[a-z0-9]+)*"
          defaultValue={c?.slug}
        />
      </label>
      <label>
        Описание
        <textarea
          name="description"
          maxLength={5000}
          defaultValue={c?.description}
        />
      </label>
      <label>
        Публикация
        <select name="status" defaultValue={c?.status || "draft"}>
          <option value="draft">Черновик</option>
          <option value="published">Опубликован</option>
        </select>
      </label>
      <button className="button">Сохранить курс</button>
      {c && (
        <button
          className="button danger"
          type="button"
          onClick={async () => {
            if (!confirm("Удалить курс, уроки, прогресс и оценки?")) return;
            try {
              await api("/staff/courses/" + c.id, "DELETE");
              location.assign("/teacher");
            } catch (e) {
              setMessage((e as Error).message);
            }
          }}
        >
          Удалить курс
        </button>
      )}
      <p role="status">{message}</p>
    </form>
  );
}
function ContentEditor({ cid }: { cid: string }) {
  const { data, error, reload } = useLoad("/courses/" + cid);
  const [message, setMessage] = useState(""),
    [editing, setEditing] = useState<Row | null>(null);
  return (
    <section className="panel spaced">
      <h2>Модули и уроки</h2>
      <State data={data} error={error} />
      {data?.modules.map((m: Row) => (
        <section className="module-editor" key={m.id}>
          <form
            className="toolbar"
            onSubmit={async (e) => {
              e.preventDefault();
              const f = new FormData(e.currentTarget);
              try {
                await api("/staff/modules/" + m.id, "PUT", {
                  title: f.get("title"),
                  position: Number(f.get("position")),
                });
                reload();
              } catch (e) {
                setMessage((e as Error).message);
              }
            }}
          >
            <label>
              Название модуля
              <input name="title" required defaultValue={m.title} />
            </label>
            <label>
              Позиция
              <input
                type="number"
                name="position"
                min={1}
                defaultValue={m.position}
                required
              />
            </label>
            <button className="button secondary">Сохранить модуль</button>
            <button
              type="button"
              className="button danger"
              onClick={async () => {
                if (!confirm("Удалить модуль со всеми уроками?")) return;
                try {
                  await api("/staff/modules/" + m.id, "DELETE");
                  reload();
                } catch (e) {
                  setMessage((e as Error).message);
                }
              }}
            >
              Удалить
            </button>
          </form>
          {data.items
            .filter((l: Row) => l.module_id === m.id)
            .map((l: Row) => (
              <div className="lesson-row" key={l.id}>
                <strong>
                  {l.position}. {l.title}
                </strong>
                <button
                  className="text-button"
                  onClick={async () => {
                    try {
                      setEditing({
                        ...(await api("/lessons/" + l.id)),
                        module_id: m.id,
                        position: l.position,
                      });
                    } catch (e) {
                      setMessage((e as Error).message);
                    }
                  }}
                >
                  Редактировать →
                </button>
                <button
                  className="text-button"
                  onClick={async () => {
                    if (!confirm("Удалить урок, его прогресс и оценки?"))
                      return;
                    try {
                      await api("/staff/lessons/" + l.id, "DELETE");
                      reload();
                    } catch (e) {
                      setMessage((e as Error).message);
                    }
                  }}
                >
                  Удалить
                </button>
              </div>
            ))}
          <button
            className="button secondary"
            onClick={() =>
              setEditing({
                module_id: m.id,
                position:
                  Math.max(
                    0,
                    ...data.items
                      .filter((l: Row) => l.module_id === m.id)
                      .map((l: Row) => l.position),
                  ) + 1,
              })
            }
          >
            Добавить урок
          </button>
        </section>
      ))}
      <form
        className="editor spaced"
        onSubmit={async (e) => {
          e.preventDefault();
          const form = e.currentTarget,
            f = new FormData(form);
          try {
            await api(`/staff/courses/${cid}/modules`, "POST", {
              title: f.get("title"),
              position: Number(f.get("position")),
            });
            form.reset();
            reload();
          } catch (e) {
            setMessage((e as Error).message);
          }
        }}
      >
        <h3>Новый модуль</h3>
        <label>
          Название
          <input name="title" required />
        </label>
        <label>
          Порядок
          <input type="number" name="position" min={1} required />
        </label>
        <button className="button">Добавить модуль</button>
      </form>
      {editing && (
        <LessonEditor
          key={editing.id || "new" + editing.module_id}
          lesson={editing}
          onSave={() => {
            setEditing(null);
            reload();
          }}
        />
      )}
      <p role="status">{message}</p>
    </section>
  );
}
function LessonEditor({
  lesson: l,
  onSave,
}: {
  lesson: Row;
  onSave: () => void;
}) {
  const [message, setMessage] = useState("");
  return (
    <form
      className="editor panel spaced"
      onSubmit={async (e) => {
        e.preventDefault();
        const f = new FormData(e.currentTarget),
          data = Object.fromEntries(f) as Row;
        for (const key of ["position", "duration_minutes"])
          data[key] = Number(data[key]);
        data.video_url = data.video_url || null;
        data.video_duration = data.video_duration
          ? Number(data.video_duration)
          : null;
        try {
          await api(
            l.id
              ? "/staff/lessons/" + l.id
              : `/staff/modules/${l.module_id}/lessons`,
            l.id ? "PUT" : "POST",
            data,
          );
          onSave();
        } catch (e) {
          setMessage((e as Error).message);
        }
      }}
    >
      <h3>{l.id ? "Редактирование" : "Новый урок"}</h3>
      {[
        ["title", "Название"],
        ["summary", "Краткое описание"],
        ["position", "Порядок"],
        ["duration_minutes", "Длительность, минут"],
        ["video_url", "Проверенный URL HTML5 видео (не iframe)"],
        ["video_duration", "Точная длительность видео, секунд"],
      ].map(([key, label]) => (
        <label key={key}>
          {label}
          <input
            name={key}
            type={
              ["position", "duration_minutes", "video_duration"].includes(key)
                ? "number"
                : "text"
            }
            min={1}
            required={["title", "position", "duration_minutes"].includes(key)}
            defaultValue={l[key] ?? (key === "duration_minutes" ? 15 : "")}
          />
        </label>
      ))}
      <label>
        Учебный текст
        <textarea name="content" rows={10} defaultValue={l.content} />
      </label>
      <label>
        Практика
        <textarea name="practice" rows={3} defaultValue={l.practice} />
      </label>
      <p className="micro">
        При замене видео прежний прогресс сбрасывается. Внешние iframe не
        поддерживаются.
      </p>
      <button className="button">Сохранить урок</button>
      <button className="button secondary" type="button" onClick={onSave}>
        Закрыть
      </button>
      <p role="status">{message}</p>
    </form>
  );
}
function Admin() {
  const { data, error } = useLoad("/admin/users");
  return (
    <>
      <Heading
        title="Пользователи"
        text="Учётные записи и роли. Повышение роли через профиль запрещено."
      />
      <State data={data} error={error} />
      {data?.map((u: Row) => (
        <div className="lesson-row" key={u.id}>
          <strong>{u.display_name}</strong>
          <span>
            {u.email} · {u.role}
          </span>
        </div>
      ))}
    </>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
