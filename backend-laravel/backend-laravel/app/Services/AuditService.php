<?php

namespace App\Services;

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;

class AuditService
{
    protected string $apiUrl;

    public function __construct()
    {
        $this->apiUrl = config('services.python_api.url', 'http://127.0.0.1:8000');
    }

    public function analyze(UploadedFile $file): array
    {
        try {
            $response = Http::timeout(120) 
                ->attach(
                    'file', 
                    file_get_contents($file->getPathname()), 
                    $file->getClientOriginalName()
                )
                ->post("{$this->apiUrl}/check_epicrisis");

            if ($response->successful()) {
                return $response->json();
            }

            throw new \Exception('Python API error: ' . $response->body());
            
        } catch (\Exception $e) {
            throw new \Exception('Ошибка связи с сервисом анализа: ' . $e->getMessage());
        }
    }
}