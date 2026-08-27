<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Controllers\Api\Concerns\RespondsWithJson;
use App\Models\Proyecto;
use App\Models\Tarea;
use App\Models\Usuario;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

class TareaController extends Controller
{
    use RespondsWithJson;

    private const ESTADOS = ['Por Hacer', 'Pendiente', 'En Progreso', 'En Revision', 'En Revisión', 'Completada', 'Hecho'];

    public function index(Request $request)
    {
        $query = Tarea::with(['proyecto:id_proyecto,nombre,id_empresa', 'usuario:id_usuario,nombres,apellidos,avatar'])
            ->whereHas('proyecto', fn ($q) => $q->where('id_empresa', $request->user()->id_empresa));

        if ($request->filled('proyecto_id')) {
            $query->where('id_proyecto', $request->integer('proyecto_id'));
        }

        if ($request->filled('estado') && in_array($request->string('estado')->toString(), self::ESTADOS, true)) {
            $query->where('estado', $request->string('estado'));
        }

        if ($request->filled('q')) {
            $query->where('titulo', 'like', '%'.$request->string('q').'%');
        }

        if ($request->boolean('vencidas')) {
            $query->whereDate('fecha_vencimiento', '<', now()->toDateString())->where('estado', '<>', 'Completada');
        }

        $tareas = $query
            ->orderByRaw('fecha_vencimiento IS NULL')
            ->orderBy('fecha_vencimiento')
            ->orderByDesc('id_tarea')
            ->paginate(min($request->integer('limit', 100), 500));

        return $this->success($tareas, 'Tareas obtenidas');
    }

    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'titulo' => ['required', 'string', 'min:5', 'max:200'],
            'descripcion' => ['nullable', 'string'],
            'estado' => ['nullable', Rule::in(self::ESTADOS)],
            'fecha_vencimiento' => ['nullable', 'date'],
            'id_proyecto' => ['required_without:proyecto_id', 'integer'],
            'proyecto_id' => ['required_without:id_proyecto', 'integer'],
            'id_usuario' => ['nullable', 'integer'],
            'id_equipo' => ['nullable', 'integer'],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $proyectoId = $request->integer('id_proyecto') ?: $request->integer('proyecto_id');
        $proyecto = Proyecto::where('id_empresa', $request->user()->id_empresa)->find($proyectoId);

        if (! $proyecto) {
            return $this->error('No tiene permiso para agregar tareas a este proyecto', 403);
        }

        $asignadoId = $request->integer('id_usuario') ?: $request->user()->id_usuario;
        $asignado = Usuario::where('id_empresa', $request->user()->id_empresa)->find($asignadoId);

        $tarea = Tarea::create([
            'titulo' => $request->titulo,
            'descripcion' => $request->input('descripcion'),
            'estado' => $request->input('estado', 'Por Hacer'),
            'fecha_vencimiento' => $request->input('fecha_vencimiento'),
            'id_proyecto' => $proyecto->id_proyecto,
            'id_usuario' => $asignado?->id_usuario ?? $request->user()->id_usuario,
            'id_equipo' => $request->input('id_equipo'),
            'fecha_creacion' => now(),
        ]);

        return $this->success($tarea, 'Tarea creada exitosamente', 201);
    }

    public function show(Request $request, string $id)
    {
        $tarea = Tarea::with(['proyecto', 'usuario'])
            ->whereHas('proyecto', fn ($q) => $q->where('id_empresa', $request->user()->id_empresa))
            ->find($id);

        if (! $tarea) {
            return $this->error('Tarea no encontrada', 404);
        }

        return $this->success($tarea);
    }

    public function update(Request $request, string $id)
    {
        $tarea = Tarea::whereHas('proyecto', fn ($q) => $q->where('id_empresa', $request->user()->id_empresa))->find($id);

        if (! $tarea) {
            return $this->error('Tarea no encontrada', 404);
        }

        $validator = Validator::make($request->all(), [
            'titulo' => ['sometimes', 'string', 'min:5', 'max:200'],
            'descripcion' => ['nullable', 'string'],
            'estado' => ['sometimes', Rule::in(self::ESTADOS)],
            'fecha_vencimiento' => ['nullable', 'date'],
            'id_proyecto' => ['sometimes', 'integer'],
            'proyecto_id' => ['sometimes', 'integer'],
            'id_usuario' => ['nullable', 'integer'],
            'id_equipo' => ['nullable', 'integer'],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $data = $validator->validated();
        $proyectoId = $request->integer('id_proyecto') ?: $request->integer('proyecto_id');

        if ($proyectoId) {
            $proyecto = Proyecto::where('id_empresa', $request->user()->id_empresa)->find($proyectoId);
            if (! $proyecto) {
                return $this->error('No tiene permiso para mover la tarea a este proyecto', 403);
            }
            $data['id_proyecto'] = $proyecto->id_proyecto;
        }

        unset($data['proyecto_id']);

        if (array_key_exists('id_usuario', $data) && $data['id_usuario']) {
            $asignado = Usuario::where('id_empresa', $request->user()->id_empresa)->find($data['id_usuario']);
            $data['id_usuario'] = $asignado?->id_usuario ?? $request->user()->id_usuario;
        }

        $tarea->update($data);

        return $this->success($tarea->fresh(['proyecto', 'usuario']), 'Tarea actualizada');
    }

    public function destroy(Request $request, string $id)
    {
        $deleted = Tarea::whereHas('proyecto', fn ($q) => $q->where('id_empresa', $request->user()->id_empresa))
            ->where('id_tarea', $id)
            ->delete();

        if (! $deleted) {
            return $this->error('Tarea no encontrada', 404);
        }

        return $this->success(null, 'Tarea eliminada correctamente');
    }

    public function init(Request $request)
    {
        $usuario = $request->user()->load(['empresa', 'rol']);
        $proyectos = Proyecto::where('id_empresa', $usuario->id_empresa)->orderBy('nombre')->get(['id_proyecto', 'nombre']);
        $tareas = Tarea::with(['proyecto:id_proyecto,nombre', 'usuario:id_usuario,nombres,apellidos,avatar'])
            ->whereHas('proyecto', fn ($q) => $q->where('id_empresa', $usuario->id_empresa))
            ->orderByRaw('estado = "Completada"')
            ->orderByRaw('fecha_vencimiento IS NULL')
            ->orderBy('fecha_vencimiento')
            ->get();

        $stats = [
            'total' => $tareas->count(),
            'completadas' => $tareas->where('estado', 'Completada')->count(),
            'en_progreso' => $tareas->where('estado', 'En Progreso')->count(),
            'vencidas' => $tareas->filter(fn ($t) => $t->fecha_vencimiento && $t->fecha_vencimiento < now()->toDateString() && $t->estado !== 'Completada')->count(),
        ];

        return $this->success([
            'usuario' => [
                'id_usuario' => $usuario->id_usuario,
                'nombres' => $usuario->nombres,
                'apellidos' => $usuario->apellidos,
                'cargo' => $usuario->cargo,
                'avatar' => $usuario->avatar,
                'nombre_empresa' => $usuario->empresa?->nombre,
                'nombre_rol' => $usuario->rol?->nombre,
                'iniciales' => $this->initials(trim($usuario->nombres.' '.$usuario->apellidos)),
            ],
            'proyectos' => $proyectos,
            'tareas' => $tareas,
            'stats' => $stats,
        ], 'Datos cargados');
    }

    public function mover(Request $request, string $id)
    {
        $request->merge(['estado' => [
            'pendiente' => 'Por Hacer',
            'en_progreso' => 'En Progreso',
            'en_revision' => 'En Revision',
            'hecho' => 'Completada',
        ][$request->input('estado')] ?? $request->input('estado')]);

        return $this->update($request, $id);
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
