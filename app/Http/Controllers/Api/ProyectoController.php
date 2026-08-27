<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Controllers\Api\Concerns\RespondsWithJson;
use App\Models\Proyecto;
use App\Models\Tarea;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

class ProyectoController extends Controller
{
    use RespondsWithJson;

    private const ESTADOS = ['Activo', 'Pendiente', 'En Progreso', 'Completado', 'Cancelado', 'En Espera'];

    public function index(Request $request)
    {
        $query = Proyecto::with('equipo')
            ->withCount([
                'tareas as total_tareas',
                'tareas as tareas_completadas' => fn ($q) => $q->whereIn('estado', ['Completada', 'Hecho']),
            ])
            ->where('id_empresa', $request->user()->id_empresa);

        if ($request->filled('estado')) {
            $query->where('estado', $request->string('estado'));
        }

        $proyectos = $query->orderByDesc('id_proyecto')->get()->map(fn (Proyecto $proyecto) => $this->formatProyecto($proyecto));

        return $this->success(['proyectos' => $proyectos, 'total' => $proyectos->count()], 'Proyectos cargados correctamente');
    }

    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'nombre' => ['required', 'string', 'max:150'],
            'descripcion' => ['nullable', 'string'],
            'estado' => ['nullable', Rule::in(self::ESTADOS)],
            'nivel_importancia' => ['nullable', 'integer', 'min:1', 'max:5'],
            'tipo_proyecto' => ['nullable', 'string', 'max:50'],
            'fecha_inicio' => ['nullable', 'date'],
            'fecha_fin' => ['nullable', 'date', 'after_or_equal:fecha_inicio'],
            'id_equipo' => ['nullable', 'integer', Rule::exists('equipos', 'id_equipo')->where('id_empresa', $request->user()->id_empresa)],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $proyecto = Proyecto::create($validator->safe()->merge([
            'estado' => $request->input('estado', 'Activo'),
            'nivel_importancia' => $request->integer('nivel_importancia', 1),
            'fecha_inicio' => $request->input('fecha_inicio', now()->toDateString()),
            'id_empresa' => $request->user()->id_empresa,
        ])->all());

        return $this->success($this->formatProyecto($proyecto->load('equipo')->loadCount('tareas')), 'Proyecto creado exitosamente', 201);
    }

    public function show(Request $request, string $id)
    {
        $proyecto = Proyecto::with(['equipo', 'tareas.usuario'])
            ->where('id_empresa', $request->user()->id_empresa)
            ->find($id);

        if (! $proyecto) {
            return $this->error('Proyecto no encontrado', 404);
        }

        return $this->success(['proyecto' => $proyecto], 'Proyecto cargado correctamente');
    }

    public function update(Request $request, string $id)
    {
        $proyecto = Proyecto::where('id_empresa', $request->user()->id_empresa)->find($id);

        if (! $proyecto) {
            return $this->error('Proyecto no encontrado', 404);
        }

        $validator = Validator::make($request->all(), [
            'nombre' => ['sometimes', 'string', 'max:150'],
            'descripcion' => ['nullable', 'string'],
            'estado' => ['sometimes', Rule::in(self::ESTADOS)],
            'nivel_importancia' => ['sometimes', 'integer', 'min:1', 'max:5'],
            'tipo_proyecto' => ['nullable', 'string', 'max:50'],
            'fecha_inicio' => ['nullable', 'date'],
            'fecha_fin' => ['nullable', 'date', 'after_or_equal:fecha_inicio'],
            'id_equipo' => ['nullable', 'integer', Rule::exists('equipos', 'id_equipo')->where('id_empresa', $request->user()->id_empresa)],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $proyecto->update($validator->validated());

        return $this->success($this->formatProyecto($proyecto->fresh('equipo')->loadCount('tareas')), 'Proyecto actualizado exitosamente');
    }

    public function destroy(Request $request, string $id)
    {
        $deleted = Proyecto::where('id_empresa', $request->user()->id_empresa)->whereKey($id)->delete();

        if (! $deleted) {
            return $this->error('Proyecto no encontrado', 404);
        }

        return $this->success(null, 'Proyecto eliminado correctamente');
    }

    public function cambiarEstado(Request $request, string $id)
    {
        $validator = Validator::make($request->all(), [
            'estado' => ['required', Rule::in(self::ESTADOS)],
        ]);

        if ($validator->fails()) {
            return $this->error('Estado no valido', 422, $validator->errors()->toArray());
        }

        $proyecto = Proyecto::where('id_empresa', $request->user()->id_empresa)->find($id);

        if (! $proyecto) {
            return $this->error('Proyecto no encontrado', 404);
        }

        $proyecto->update(['estado' => $request->estado]);

        return $this->success(['id' => $proyecto->id_proyecto, 'estado' => $proyecto->estado], 'Estado actualizado correctamente');
    }

    public function kanban(Request $request, string $id)
    {
        $proyecto = Proyecto::with(['tareas.usuario'])
            ->where('id_empresa', $request->user()->id_empresa)
            ->find($id);

        if (! $proyecto) {
            return $this->error('Proyecto no encontrado', 404);
        }

        $kanban = [
            'proyecto' => [
                'id' => $proyecto->id_proyecto,
                'nombre' => $proyecto->nombre,
                'estado' => $proyecto->estado,
            ],
            'columnas' => [
                'pendiente' => ['titulo' => 'Pendiente', 'tareas' => [], 'total' => 0],
                'en_progreso' => ['titulo' => 'En progreso', 'tareas' => [], 'total' => 0],
                'en_revision' => ['titulo' => 'En revision', 'tareas' => [], 'total' => 0],
                'hecho' => ['titulo' => 'Hecho', 'tareas' => [], 'total' => 0],
            ],
        ];

        $map = [
            'Por Hacer' => 'pendiente',
            'Pendiente' => 'pendiente',
            'En Progreso' => 'en_progreso',
            'En Revision' => 'en_revision',
            'En Revisión' => 'en_revision',
            'Revision' => 'en_revision',
            'Revisión' => 'en_revision',
            'Completada' => 'hecho',
            'Hecho' => 'hecho',
        ];

        foreach ($proyecto->tareas as $tarea) {
            $column = $map[$tarea->estado] ?? 'pendiente';
            $usuario = $tarea->usuario;
            $nombre = $usuario ? trim($usuario->nombres.' '.$usuario->apellidos) : 'Sin asignar';

            $kanban['columnas'][$column]['tareas'][] = [
                'id' => $tarea->id_tarea,
                'titulo' => $tarea->titulo,
                'descripcion' => $tarea->descripcion,
                'estado' => $tarea->estado,
                'fecha_creacion' => $tarea->fecha_creacion,
                'fecha_vencimiento' => $tarea->fecha_vencimiento,
                'asignado' => [
                    'id' => $tarea->id_usuario,
                    'nombre' => $nombre,
                    'iniciales' => $this->initials($nombre),
                    'avatar' => $usuario?->avatar,
                ],
                'vencida' => $tarea->fecha_vencimiento && $tarea->fecha_vencimiento < now()->toDateString(),
            ];
        }

        foreach ($kanban['columnas'] as $key => $column) {
            $kanban['columnas'][$key]['total'] = count($column['tareas']);
        }

        return $this->success($kanban, 'Kanban cargado correctamente');
    }

    private function formatProyecto(Proyecto $proyecto): array
    {
        $total = (int) ($proyecto->total_tareas ?? $proyecto->tareas_count ?? 0);
        $completadas = (int) ($proyecto->tareas_completadas ?? 0);
        $colors = [
            'Activo' => '#10b981',
            'Pendiente' => '#f59e0b',
            'En Progreso' => '#3b82f6',
            'Completado' => '#6366f1',
            'Cancelado' => '#ef4444',
            'En Espera' => '#8b5cf6',
        ];

        return [
            'id' => $proyecto->id_proyecto,
            'nombre' => $proyecto->nombre,
            'descripcion' => $proyecto->descripcion,
            'estado' => $proyecto->estado ?? 'Activo',
            'color_estado' => $colors[$proyecto->estado] ?? '#6b7280',
            'importancia' => (int) $proyecto->nivel_importancia,
            'tipo' => $proyecto->tipo_proyecto,
            'equipo' => $proyecto->equipo?->nombre,
            'fecha_inicio' => $proyecto->fecha_inicio,
            'fecha_fin' => $proyecto->fecha_fin,
            'total_tareas' => $total,
            'tareas_completadas' => $completadas,
            'porcentaje' => $total > 0 ? (int) round(($completadas / $total) * 100) : 0,
        ];
    }

    private function initials(string $name): string
    {
        $initials = collect(explode(' ', trim($name)))
            ->filter()
            ->map(fn ($part) => mb_strtoupper(mb_substr($part, 0, 1)))
            ->implode('');

        return mb_substr($initials, 0, 2) ?: 'SA';
    }
}
