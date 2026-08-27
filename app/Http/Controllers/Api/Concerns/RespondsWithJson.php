<?php

namespace App\Http\Controllers\Api\Concerns;

use Illuminate\Http\JsonResponse;

trait RespondsWithJson
{
    protected function success(mixed $data = null, string $message = 'Operacion exitosa', int $code = 200): JsonResponse
    {
        return response()->json([
            'success' => true,
            'status_code' => $code,
            'message' => $message,
            'data' => $data,
            'timestamp' => now()->toIso8601String(),
            'errors' => [],
        ], $code);
    }

    protected function error(string $message, int $code = 400, array $errors = []): JsonResponse
    {
        return response()->json([
            'success' => false,
            'status_code' => $code,
            'message' => $message,
            'data' => null,
            'timestamp' => now()->toIso8601String(),
            'errors' => $errors,
        ], $code);
    }
}
